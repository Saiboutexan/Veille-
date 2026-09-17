# -*- coding: utf-8 -*-
"""
Collecte : lit les flux des medias guineens, classe les articles par theme
et les enregistre dans veille.db (SQLite).

Usage :  python collecte.py
Relancer autant de fois que voulu : les doublons sont ignores (le lien est unique).
"""
import os
import re
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests

from sources import SOURCES, THEMES, AUTRE

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veille.db")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
ATOM = "{http://www.w3.org/2005/Atom}"


# --------------------------------------------------------------- base
def base():
    cx = sqlite3.connect(DB)
    cx.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            source      TEXT NOT NULL,
            fiabilite   TEXT NOT NULL,
            titre       TEXT NOT NULL,
            lien        TEXT NOT NULL UNIQUE,
            date_pub    TEXT,
            resume      TEXT,
            theme       TEXT NOT NULL,
            collecte_le TEXT NOT NULL
        )""")
    cx.commit()
    return cx


# --------------------------------------------------------------- outils
def sans_accent(txt):
    txt = unicodedata.normalize("NFD", txt.lower())
    return "".join(c for c in txt if unicodedata.category(c) != "Mn")


def sans_html(txt):
    txt = re.sub(r"<[^>]+>", " ", txt or "")
    txt = re.sub(r"&[a-zA-Z#0-9]+;", " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def resume_propre(txt, limite=300):
    """Enleve les residus WordPress et coupe proprement le resume."""
    t = sans_html(txt)
    # "L'article X est apparu en premier sur Y." / "The post ... appeared first on ..."
    t = re.sub(r"L[’']article\s.*?est apparu en premier sur.*$", "", t, flags=re.I)
    t = re.sub(r"The post\s.*?appeared first on.*$", "", t, flags=re.I)
    t = re.sub(r"L[’']article\s.{0,120}$", "", t, flags=re.I)   # phrase tronquee en fin
    t = re.sub(r"\[\s*[.…]*\s*\]", "…", t)                      # "[…]" ou "[ ]"
    t = re.sub(r"(Lire la suite|Continue reading|Read more).*$", "", t, flags=re.I)
    t = re.sub(r"\s+", " ", t).strip(" …-–—|")
    if len(t) > limite:
        t = t[:limite].rsplit(" ", 1)[0] + "…"
    return t


# mots-cles pre-compiles : on cherche le MOT ENTIER, pas un fragment
# (sinon "elimine" contient "mine" et "tresor" contient "or")
_MOTIFS = {
    theme: [re.compile(r"\b" + re.escape(sans_accent(m)) + r"\b") for m in mots]
    for theme, mots in THEMES.items()
}


def classer(titre, resume):
    """Range l'article dans le premier theme dont un mot-cle apparait."""
    texte = sans_accent(titre + " " + resume)
    for theme, motifs in _MOTIFS.items():
        for motif in motifs:
            if motif.search(texte):
                return theme
    return AUTRE


def date_iso(txt):
    if not txt:
        return None
    try:
        d = parsedate_to_datetime(txt)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return txt[:16]


def texte(el, *noms):
    for n in noms:
        trouve = el.find(n)
        if trouve is not None and (trouve.text or "").strip():
            return trouve.text.strip()
        if trouve is not None and trouve.get("href"):      # Atom <link href=...>
            return trouve.get("href")
    return ""


# --------------------------------------------------------------- collecte
def lire_flux(url):
    """Renvoie la liste des entrees d'un flux RSS ou Atom."""
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    # certains flux contiennent des entites HTML que XML refuse (&nbsp; ...)
    contenu = r.content.decode("utf-8", "ignore")
    contenu = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", contenu)
    racine = ET.fromstring(contenu)
    entrees = racine.findall(".//item")
    if entrees:
        return [{"titre": texte(e, "title"),
                 "lien": texte(e, "link"),
                 "date": texte(e, "pubDate"),
                 "resume": texte(e, "description")} for e in entrees]
    return [{"titre": texte(e, ATOM + "title"),
             "lien": texte(e, ATOM + "link"),
             "date": texte(e, ATOM + "updated", ATOM + "published"),
             "resume": texte(e, ATOM + "summary", ATOM + "content")}
            for e in racine.findall(".//" + ATOM + "entry")]


def collecter():
    cx = base()
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_nouveaux, en_panne = 0, []

    print("Collecte du %s\n" % maintenant)
    print("%-18s %8s %9s   %s" % ("SOURCE", "LUS", "NOUVEAUX", "ETAT"))
    print("-" * 58)

    for src in SOURCES:
        try:
            entrees = lire_flux(src["flux"])
        except Exception as e:
            en_panne.append(src["nom"])
            print("%-18s %8s %9s   %s" % (src["nom"], "-", "-", str(e)[:22]))
            continue

        nouveaux = 0
        for e in entrees:
            lien = (e["lien"] or "").strip()
            titre = sans_html(e["titre"])
            if not lien or not titre:
                continue
            resume = resume_propre(e["resume"])
            cur = cx.execute(
                "INSERT OR IGNORE INTO articles "
                "(source, fiabilite, titre, lien, date_pub, resume, theme, collecte_le) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (src["nom"], src["fiabilite"], titre, lien, date_iso(e["date"]),
                 resume, classer(titre, resume), maintenant))
            nouveaux += cur.rowcount
        cx.commit()
        total_nouveaux += nouveaux
        print("%-18s %8d %9d   ok" % (src["nom"], len(entrees), nouveaux))

    total = cx.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    print("-" * 58)
    print("%d nouveaux articles  |  %d en base" % (total_nouveaux, total))
    if en_panne:
        print("Sources injoignables : " + ", ".join(en_panne))

    print("\nRepartition par theme :")
    for theme, n in cx.execute(
            "SELECT theme, COUNT(*) FROM articles GROUP BY theme ORDER BY 2 DESC"):
        print("   %-32s %4d" % (theme, n))
    cx.close()
    print("\nBase : %s\nDashboard : streamlit run app.py" % DB)


def reclasser():
    """Reapplique le classement ET le nettoyage des resumes sur toute la base.
    A lancer apres avoir modifie les mots-cles dans sources.py :
        python collecte.py --reclasser
    """
    cx = base()
    lignes = cx.execute("SELECT id, titre, resume FROM articles").fetchall()
    change = 0
    for i, titre, resume in lignes:
        propre = resume_propre(resume or "")
        theme = classer(titre, propre)
        cur = cx.execute(
            "UPDATE articles SET theme = ?, resume = ? "
            "WHERE id = ? AND (theme != ? OR resume != ?)",
            (theme, propre, i, theme, propre))
        change += cur.rowcount
    cx.commit()
    print("%d articles mis a jour sur %d" % (change, len(lignes)))
    for theme, n in cx.execute(
            "SELECT theme, COUNT(*) FROM articles GROUP BY theme ORDER BY 2 DESC"):
        print("   %-32s %4d" % (theme, n))
    cx.close()


if __name__ == "__main__":
    import sys
    if "--reclasser" in sys.argv:
        reclasser()
    else:
        collecter()
