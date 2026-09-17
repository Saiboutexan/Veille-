# -*- coding: utf-8 -*-
"""
Collecte des appels d'offres et opportunites concernant la Guinee.

Deux origines :
  1. Banque mondiale  - API publique, avis structures (le plus fiable)
  2. Presse guineenne - les avis publies dans les flux deja collectes

Usage :  python offres.py
"""
import hashlib
import html
import os
import re
import sqlite3
from datetime import datetime

import requests

from collecte import DB, UA, base, sans_accent, sans_html
from sources import MOTS_AVIS, DOMAINES, LIEUX_GUINEE

WB_API = "https://search.worldbank.org/api/v2/procnotices"
WB_LIEN = "https://projects.worldbank.org/en/projects-operations/procurement-detail/%s"
PAGES = 3          # 3 x 1000 avis ~ les 25 derniers jours. Monter si besoin.

# un marche deja attribue n'est pas une opportunite : on ne le garde pas
TYPES_EXCLUS = ("contract award",)


# --------------------------------------------------------------- base
def base_offres():
    cx = base()
    cx.execute("""
        CREATE TABLE IF NOT EXISTS offres (
            id          TEXT PRIMARY KEY,
            origine     TEXT NOT NULL,
            titre       TEXT NOT NULL,
            domaine     TEXT,
            zone        TEXT,
            criteres    TEXT,
            budget      TEXT,
            date_limite TEXT,
            limite_iso  TEXT,
            publie_le   TEXT,
            lien        TEXT,
            collecte_le TEXT NOT NULL
        )""")
    # migration douce si la base vient d'une version anterieure
    colonnes = [c[1] for c in cx.execute("PRAGMA table_info(offres)")]
    if "limite_iso" not in colonnes:
        cx.execute("ALTER TABLE offres ADD COLUMN limite_iso TEXT")

    # v2 : les identifiants venaient de hash(), qui change a chaque execution
    # de Python. Le meme avis revenait donc en double a chaque collecte. On
    # purge une seule fois les lignes portant ces anciens identifiants : la
    # collecte suivante les recree avec un identifiant stable.
    if cx.execute("PRAGMA user_version").fetchone()[0] < 2:
        cx.execute("DELETE FROM offres WHERE id LIKE 'PRESSE-%' OR id LIKE 'BAILLEUR-%'")
        cx.execute("PRAGMA user_version = 2")
    cx.commit()
    return cx


def identifiant(prefixe, lien):
    """Identifiant stable d'un avis : la meme adresse donne toujours le meme
    identifiant, donc jamais de doublon d'une collecte a l'autre."""
    return "%s-%s" % (prefixe, hashlib.md5(lien.encode("utf-8")).hexdigest()[:16])


# --------------------------------------------------------------- extraction
def domaine_de(texte):
    """Devine le domaine concerne a partir du libelle de l'avis."""
    t = sans_accent(texte)
    for domaine, mots in DOMAINES.items():
        for mot in mots:
            if re.search(r"\b" + re.escape(sans_accent(mot)) + r"\b", t):
                return domaine
    return "Non précisé"


def zone_de(texte, pays="Guinée"):
    """Cherche les prefectures / regions guineennes citees dans l'avis."""
    t = sans_accent(texte)
    trouves = [lieu for lieu in LIEUX_GUINEE
               if re.search(r"\b" + re.escape(sans_accent(lieu)) + r"\b", t)]
    if trouves:
        vus = list(dict.fromkeys(trouves))[:4]
        return ", ".join(vus)
    return "%s (zone non précisée)" % pays


MONTANT = re.compile(
    r"((?:[\d][\d\s.,]{2,})\s*(?:millions?|milliards?)?\s*"
    r"(?:GNF|FG|francs?\s+guin\w+|USD|\$|EUR|€|XOF|FCFA))", re.I)


def budget_de(texte):
    """Repere un montant dans le corps de l'avis."""
    for m in MONTANT.findall(texte or ""):
        propre = re.sub(r"\s+", " ", m).strip(" .,")
        if len(propre) >= 5 and any(c.isdigit() for c in propre):
            return propre
    return "Non précisé dans l'avis"


VOIR_AVIS = "Voir le détail dans l'avis (lien ci-dessous)."

# expressions qui annoncent VRAIMENT les conditions a remplir
CLES_CRITERES = ("critere de selection", "criteres de selection", "qualification requise",
                 "qualifications requises", "experience pertinente", "profil recherche",
                 "doivent fournir", "doit fournir", "eligibilite", "sont eligibles",
                 "conditions de participation", "doivent justifier", "doivent avoir",
                 "annees d'experience", "diplome", "sont invites a manifester")


def criteres_de(texte, titre="", limite=340):
    """Extrait les phrases qui enoncent les conditions a remplir."""
    texte = re.sub(r"\s+", " ", texte or "")
    if len(texte) < 120:                       # pas de corps exploitable
        return VOIR_AVIS
    phrases = re.split(r"(?<=[.;])\s+", texte)
    gardees = []
    for p in phrases:
        p = p.strip()
        if not (40 < len(p) < 400):
            continue
        if sans_accent(p)[:60] == sans_accent(titre)[:60]:   # simple echo du titre
            continue
        if any(c in sans_accent(p) for c in CLES_CRITERES):
            gardees.append(p)
    if not gardees:
        return VOIR_AVIS
    joint = " ".join(gardees[:2])
    return joint[:limite].rsplit(" ", 1)[0] + ("…" if len(joint) > limite else "")


def nettoie(txt):
    return re.sub(r"\s+", " ", sans_html(html.unescape(txt or ""))).strip()


def jolie_date(iso):
    if not iso:
        return "Non précisée"
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return iso[:10]


# --------------------------------------------------------------- Banque mondiale
def concerne_guinee(a):
    """Vrai si l'avis porte sur la Guinee (Conakry), pas sur un homonyme."""
    pays = a.get("project_ctry_name") or ""
    if pays in ("Guinea-Bissau", "Equatorial Guinea", "Papua New Guinea"):
        return False
    if pays == "Guinea":
        return True
    contexte = " ".join([nettoie(a.get("bid_description")),
                         nettoie(a.get("project_name")),
                         nettoie(a.get("contact_address"))])
    return bool(re.search(r"\bguin[ée]e?\b", sans_accent(contexte)))


def banque_mondiale(pages=PAGES):
    """Recupere les avis recents et garde ceux qui concernent la Guinee.

    Le tri se fait page par page : on ne garde jamais les 1000 avis d'une page
    en memoire, seulement la poignee qui concerne la Guinee.
    """
    avis = []
    for page in range(pages):
        url = ("%s?format=json&rows=1000&os=%d&srt=noticedate&order=desc"
               % (WB_API, page * 1000))
        r = requests.get(url, headers={"User-Agent": UA}, timeout=90)
        r.raise_for_status()
        lot = r.json().get("procnotices", [])
        if not lot:
            break
        avis += [a for a in lot if concerne_guinee(a)]
        del lot

    retenus = []
    for a in avis:
        pays = (a.get("project_ctry_name") or "")
        corps = nettoie(a.get("notice_text"))
        libelle = nettoie(a.get("bid_description")) or nettoie(a.get("project_name"))
        contexte = " ".join([pays, libelle, nettoie(a.get("contact_address")),
                             nettoie(a.get("project_name"))])
        type_avis = a.get("notice_type") or "avis"
        if any(x in type_avis.lower() for x in TYPES_EXCLUS):
            continue                                  # marche deja attribue

        deadline = a.get("submission_deadline_date")
        heure = a.get("submission_deadline_time")
        retenus.append({
            "id": "WB-" + str(a.get("id")),
            "origine": "Banque mondiale — %s" % type_avis,
            "titre": libelle or "Avis sans intitulé",
            "domaine": domaine_de(libelle + " " + corps[:600]),
            "zone": zone_de(contexte + " " + corps[:1500]),
            "criteres": criteres_de(corps, libelle),
            "budget": budget_de(corps),
            "date_limite": jolie_date(deadline) + (" à %s" % heure if heure else ""),
            "limite_iso": (deadline or "")[:10],
            "publie_le": a.get("noticedate") or "",
            "lien": WB_LIEN % a.get("id"),
        })
    return retenus


# --------------------------------------------------------------- presse
def presse(cx):
    """Repere les avis publies dans les articles deja collectes."""
    motifs = [re.compile(r"\b" + re.escape(sans_accent(m))) for m in MOTS_AVIS]
    retenus = []
    for lien, titre, resume, source, date_pub in cx.execute(
            "SELECT lien, titre, resume, source, date_pub FROM articles"):
        texte = sans_accent(titre + " " + (resume or ""))
        if not any(m.search(texte) for m in motifs):
            continue
        corps = titre + ". " + (resume or "")
        retenus.append({
            "id": identifiant("PRESSE", lien),
            "origine": "Presse guinéenne — %s" % source,
            "titre": titre,
            "domaine": domaine_de(corps),
            "zone": zone_de(corps),
            "criteres": criteres_de(corps, titre),
            "budget": budget_de(corps),
            "date_limite": "Voir l'avis",
            "limite_iso": "",
            "publie_le": date_pub or "",
            "lien": lien,
        })
    return retenus


# --------------------------------------------------------------- collecte
def collecter_offres():
    cx = base_offres()
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("Collecte des appels d'offres — %s\n" % maintenant)

    lots = []
    try:
        wb = banque_mondiale()
        print("Banque mondiale     : %3d avis concernant la Guinée" % len(wb))
        lots += wb
    except Exception as e:
        print("Banque mondiale     : injoignable (%s)" % str(e)[:45])

    pr = presse(cx)
    print("Presse guinéenne    : %3d avis repérés dans les articles" % len(pr))
    lots += pr

    nouveaux = 0
    for o in lots:
        cur = cx.execute(
            "INSERT OR REPLACE INTO offres (id, origine, titre, domaine, zone, criteres, "
            "budget, date_limite, limite_iso, publie_le, lien, collecte_le) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (o["id"], o["origine"], o["titre"], o["domaine"], o["zone"], o["criteres"],
             o["budget"], o["date_limite"], o["limite_iso"], o["publie_le"],
             o["lien"], maintenant))
        nouveaux += cur.rowcount
    cx.commit()

    total = cx.execute("SELECT COUNT(*) FROM offres").fetchone()[0]
    print("\n%d nouveaux avis  |  %d en base" % (nouveaux, total))
    print("\nRépartition par domaine :")
    for dom, n in cx.execute(
            "SELECT domaine, COUNT(*) FROM offres GROUP BY domaine ORDER BY 2 DESC"):
        print("   %-38s %3d" % (dom, n))
    cx.close()
    print("\nRapport : python rapport.py")


if __name__ == "__main__":
    collecter_offres()
