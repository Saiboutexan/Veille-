# -*- coding: utf-8 -*-
"""
Collecte des opportunites publiees par les bailleurs et plateformes du
carnet BAILLEURS (base "appels et projets - societe civile 2026").

Deux facons de lire un guichet :
  1. son flux RSS, quand il en expose un      -> flux_bailleurs()
  2. un collecteur dedie, quand il n'en a pas -> atlas()  (Atlas des OSC)

Les guichets sans flux ni collecteur ne sont pas perdus : ils restent listes
dans la section "Ou chercher" du rapport, a consulter a la main.

Usage :  python bailleurs.py
"""
import html
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests

from collecte import UA, lire_flux, resume_propre, sans_accent, sans_html
from offres import (VOIR_AVIS, base_offres, budget_de, criteres_de, domaine_de,
                    identifiant)
from sources import BAILLEURS, LIEUX_GUINEE, MOTS_OPPORTUNITE

ATLAS_PLAN = "https://atlasdesoscgn.com/sitemap.xml"
ATLAS_MAX = 40            # nombre de fiches d'opportunites lues au maximum

_MOTIFS_OPP = [re.compile(r"\b" + re.escape(sans_accent(m))) for m in MOTS_OPPORTUNITE]


def est_une_opportunite(texte):
    """Vrai si le texte annonce un appel, un financement ou une candidature."""
    t = sans_accent(texte)
    return any(m.search(t) for m in _MOTIFS_OPP)


# --------------------------------------------------------------- dates
MOIS_FR = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
    "decembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
}

# ce qui annonce une echeance : "Date limite : ...", "deadline: ...",
# "candidatures avant le ...", "au plus tard le ..."
ANNONCE = (r"(?:date\s+limite|date\s+de\s+cloture|echeance|cloture|deadline|"
           r"closing\s+date|apply\s+by|avant\s+le|au\s+plus\s+tard)")

# Entre l'annonce et la date, la formulation varie : "date limite : 6 mai",
# "date limite de soumission est fixee au 6 mai". On tolere donc un peu de
# remplissage, mais sans chiffre : sinon on sauterait sur une autre date.
_LIAISON = r"[^\d]{0,30}?"

_JOUR_MOIS = re.compile(ANNONCE + _LIAISON + r"(\d{1,2})(?:er)?\s+([a-z]+)\s+(\d{4})")
_NUMERIQUE = re.compile(ANNONCE + _LIAISON + r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})")
_ISO = re.compile(ANNONCE + _LIAISON + r"(\d{4})-(\d{2})-(\d{2})")


def date_limite_de(texte):
    """Cherche une date de cloture dans le texte -> (libelle, AAAA-MM-JJ).

    Renvoie ("Voir l'avis", "") si aucune date n'est annoncee : mieux vaut
    pas de date du tout qu'une date fausse. L'avis original fait foi.
    """
    t = sans_accent(re.sub(r"\s+", " ", texte or ""))

    m = _JOUR_MOIS.search(t)
    if m:
        mois = MOIS_FR.get(m.group(2))
        if mois:
            try:
                d = datetime(int(m.group(3)), mois, int(m.group(1)))
                return d.strftime("%d/%m/%Y"), d.strftime("%Y-%m-%d")
            except ValueError:
                pass

    m = _NUMERIQUE.search(t)
    if m:
        try:
            d = datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            return d.strftime("%d/%m/%Y"), d.strftime("%Y-%m-%d")
        except ValueError:
            pass

    m = _ISO.search(t)
    if m:
        try:
            d = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return d.strftime("%d/%m/%Y"), d.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return "Voir l'avis", ""


def zone_bailleur(texte):
    """Zone d'un appel de bailleur : la Guinee si elle est citee, sinon
    l'appel est international et l'eligibilite depend du dossier."""
    t = sans_accent(texte)
    trouves = [lieu for lieu in LIEUX_GUINEE
               if re.search(r"\b" + re.escape(sans_accent(lieu)) + r"\b", t)]
    if trouves:
        return ", ".join(list(dict.fromkeys(trouves))[:4])
    if re.search(r"\bguine[e]?\b", t):
        return "Guinée"
    return "International (vérifier l'éligibilité dans l'avis)"


def date_flux(txt):
    """Date de publication d'une entree de flux -> AAAA-MM-JJ HH:MM."""
    if not txt:
        return ""
    try:
        return parsedate_to_datetime(txt).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return txt[:16]


# --------------------------------------------------------------- flux RSS
def flux_bailleurs(journal=True):
    """Lit les flux des bailleurs et ne garde que les entrees qui sont
    des appels : leurs flux melangent communiques, rapports et appels."""
    retenus = []
    for b in [b for b in BAILLEURS if b.get("flux")]:
        try:
            entrees = lire_flux(b["flux"])
        except Exception as e:
            if journal:
                print("   %-40s injoignable (%s)" % (b["nom"][:40], str(e)[:26]))
            continue

        gardes = 0
        for e in entrees:
            lien = (e.get("lien") or "").strip()
            titre = sans_html(e.get("titre") or "")
            if not lien or not titre:
                continue
            resume = resume_propre(e.get("resume") or "", 400)
            corps = titre + ". " + resume
            if not est_une_opportunite(corps):
                continue

            libelle, iso = date_limite_de(corps)
            # le domaine doit rester un des libelles de DOMAINES, sinon le
            # filtre par domaine eclate en autant de valeurs que de bailleurs.
            # A defaut, on classe d'apres la specialite declaree du guichet.
            domaine = domaine_de(corps)
            if domaine == "Non précisé":
                domaine = domaine_de(b["domaines"] or "")
            retenus.append({
                "id": identifiant("BAILLEUR", lien),
                "origine": "Bailleur — %s" % b["nom"],
                "titre": titre,
                "domaine": domaine,
                "zone": zone_bailleur(corps),
                "criteres": criteres_de(corps, titre) if len(corps) > 150
                            else "Public visé : %s. Voir le détail dans l'avis."
                                 % b["cible"],
                "budget": budget_de(corps),
                "date_limite": libelle,
                "limite_iso": iso,
                "publie_le": date_flux(e.get("date")),
                "lien": lien,
            })
            gardes += 1

        if journal:
            print("   %-40s %2d appel(s) sur %2d publications"
                  % (b["nom"][:40], gardes, len(entrees)))
    return retenus


# --------------------------------------------------------------- Atlas des OSC
def _page(url, timeout=20):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    return r.text


def _meta(page, propriete):
    m = re.search(r'<meta[^>]+(?:property|name)="%s"[^>]+content="(.*?)"'
                  % propriete, page, re.S | re.I)
    return html.unescape(m.group(1)).strip() if m else ""


# Le nom du portail apparait dans l'en-tete et le pied de CHAQUE page. Sans
# cela, toute fiche serait classee "Guinee", meme une bourse mondiale.
_CHROME = re.compile(r"Atlas des OSC de Guin[ée]e", re.I)

# Fin du contenu utile : ce qui suit appartient a d'AUTRES opportunites.
# C'est la que se trouvait la "Date limite" faussement attribuee a la fiche.
_FIN_CONTENU = re.compile(r"Opportunit[ée]s similaires|Voir aussi|"
                          r"[ÀA] lire aussi|Sur le m[êe]me th[èe]me", re.I)

# Debut du contenu utile : avant, il n'y a que le menu de navigation.
_DEBUT_CONTENU = re.compile(r"Retour aux opportunit[ée]s", re.I)

_PUBLIE_LE = re.compile(r"Publi[ée]\s+le\s+(\d{1,2})(?:er)?\s+([a-zA-Zéû]+)\s+(\d{4})")
_CHAMP = r"%s\s+(.{2,90}?)\s+(?:Organisme|Public cible|Publi[ée] le|Postuler|$)"


def corps_atlas(page):
    """Le texte de la fiche seule : sans le menu, sans le pied de page et
    sans le bloc des opportunites similaires."""
    coeur = re.search(r"<main\b.*?</main>", page, re.S | re.I)
    page = coeur.group(0) if coeur else page
    page = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    texte = re.sub(r"\s+", " ", sans_html(html.unescape(page)))

    debut = _DEBUT_CONTENU.search(texte)
    if debut:
        texte = texte[debut.end():]
    fin = _FIN_CONTENU.search(texte)
    if fin:
        texte = texte[:fin.start()]
    return _CHROME.sub(" ", texte).strip()


def _champ_atlas(texte, etiquette):
    m = re.search(_CHAMP % etiquette, texte)
    return m.group(1).strip() if m else ""


def atlas(journal=True):
    """Atlas des OSC de Guinee : pas de flux RSS, mais un plan de site qui
    expose la rubrique Opportunites. On lit le plan, puis chaque fiche."""
    fiche = next((b for b in BAILLEURS if b.get("collecteur") == "atlas"), None)
    if fiche is None:
        return []

    plan = _page(ATLAS_PLAN, 30)
    liens = [u for u in re.findall(r"<loc>(.*?)</loc>", plan)
             if "/opportunites/" in u][:ATLAS_MAX]
    if journal:
        print("   %-40s %2d fiche(s) au plan du site" % (fiche["nom"][:40], len(liens)))

    retenus = []
    for url in liens:
        try:
            page = _page(url)
        except Exception:
            continue

        titre = _meta(page, "og:title") or _meta(page, "title")
        titre = re.sub(r"\s*[|·—–-]\s*Atlas des OSC.*$", "", titre).strip()
        if not titre:
            continue

        corps = corps_atlas(page)
        libelle, iso = date_limite_de(corps)

        # la fiche nomme l'organisme et le public vise : c'est plus sur que
        # de deviner les criteres dans le texte
        organisme = _champ_atlas(corps, "Organisme")
        cible = _champ_atlas(corps, "Public cible")
        criteres = criteres_de(corps, titre)
        if criteres == VOIR_AVIS and (organisme or cible):
            criteres = " ".join(filter(None, [
                "Organisme : %s." % organisme if organisme else "",
                "Public visé : %s." % cible if cible else "",
                "Conditions détaillées dans l'avis."]))

        publie = ""
        m = _PUBLIE_LE.search(corps)
        if m:
            mois = MOIS_FR.get(sans_accent(m.group(2)))
            if mois:
                try:
                    publie = datetime(int(m.group(3)), mois,
                                      int(m.group(1))).strftime("%Y-%m-%d")
                except ValueError:
                    pass

        retenus.append({
            "id": "ATLAS-" + url.rstrip("/").rsplit("/", 1)[-1][:60],
            "origine": "Atlas des OSC de Guinée",
            "titre": titre,
            "domaine": domaine_de(titre + " " + corps[:800]),
            "zone": zone_bailleur(titre + " " + corps),
            "criteres": criteres,
            "budget": budget_de(corps),
            "date_limite": libelle,
            "limite_iso": iso,
            "publie_le": publie,
            "lien": url,
        })
    return retenus


# --------------------------------------------------------------- collecte
def collecter_bailleurs():
    cx = base_offres()
    maintenant = datetime.now().strftime("%Y-%m-%d %H:%M")
    print("Collecte des opportunités des bailleurs — %s\n" % maintenant)

    lots = []
    print("Flux des bailleurs :")
    lots += flux_bailleurs()

    print("\nCollecteur dédié :")
    try:
        lots += atlas()
    except Exception as e:
        print("   Atlas des OSC de Guinée : injoignable (%s)" % str(e)[:40])

    nouveaux = 0
    for o in lots:
        cur = cx.execute(
            "INSERT OR REPLACE INTO offres (id, origine, titre, domaine, zone, "
            "criteres, budget, date_limite, limite_iso, publie_le, lien, collecte_le) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (o["id"], o["origine"], o["titre"], o["domaine"], o["zone"],
             o["criteres"], o["budget"], o["date_limite"], o["limite_iso"],
             o["publie_le"], o["lien"], maintenant))
        nouveaux += cur.rowcount
    cx.commit()

    a_la_main = [b for b in BAILLEURS if not b.get("flux") and not b.get("collecteur")]
    print("\n%d opportunité(s) retenue(s) chez les bailleurs" % len(lots))
    print("%d guichet(s) sans flux : à consulter à la main "
          "(section « Où chercher » du rapport)" % len(a_la_main))
    cx.close()


if __name__ == "__main__":
    collecter_bailleurs()
