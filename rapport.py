# -*- coding: utf-8 -*-
"""
Genere le rapport de veille en texte.

Trois sections, que l'on peut demander separement :
    1. Actualites            les articles des medias guineens
    2. Appels d'offres       les avis et opportunites ouverts
    3. Ou chercher           le carnet des guichets a consulter

Usage :
    python rapport.py                     -> les trois sections, sur 24 h
    python rapport.py --actualites        -> les actualites seules
    python rapport.py --offres            -> les appels d'offres seuls
    python rapport.py --jours 7           -> la semaine
    python rapport.py --theme "Espace civique"
"""
import argparse
import os
import re
import sqlite3
import sys
import textwrap
from datetime import datetime, timedelta

from sources import BAILLEURS, GUICHETS_A_LA_MAIN, GUICHETS_RELEVES, est_releve

ICI = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ICI, "veille.db")
DOSSIER = os.path.join(ICI, "rapports")
L = 80                                    # largeur du rapport
URGENT = 15                               # en deca, une echeance est "proche"

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

SECTIONS = ("actualites", "offres", "annuaire")


# --------------------------------------------------------------- mise en forme
def trait(car="="):
    return car * L


def titre_encadre(lignes):
    out = [trait("=")]
    for ligne in lignes:
        out.append(ligne.center(L).rstrip())
    out.append(trait("="))
    return out


def banniere(numero, titre):
    """L'en-tete d'une grande section."""
    return ["", trait("="), "%d. %s" % (numero, titre.upper()), trait("=")]


def sous_titre(texte, compte=None):
    """Un intertitre '--- TEXTE (n) ---' qui tient exactement la largeur."""
    tete = "--- %s " % texte.upper() if compte is None else \
           "--- %s (%d) " % (texte.upper(), compte)
    return ["", tete + "-" * max(3, L - len(tete)), ""]


def champ(etiquette, valeur, largeur_etiquette=20, indent=4):
    """Une ligne 'ETIQUETTE : valeur' proprement repliee."""
    valeur = " ".join(str(valeur or "—").split())
    tete = " " * indent + etiquette.ljust(largeur_etiquette) + ": "
    creux = " " * len(tete)
    return textwrap.fill(valeur, width=L, initial_indent=tete,
                         subsequent_indent=creux)


def entree(numero, titre, marge=4, suffixe=""):
    """La ligne de titre d'un article ou d'un avis, avec un repere a droite."""
    tete = "%s[%d] %s" % (" " * marge, numero, titre)
    ligne = textwrap.fill(tete, width=L - len(suffixe),
                          subsequent_indent=" " * (marge + 4))
    if suffixe:
        derniere = ligne.rsplit("\n", 1)[-1]
        ligne += " " * max(1, L - len(derniere) - len(suffixe)) + suffixe
    return ligne


def ligne_sommaire(texte, valeur):
    """'  1. Actualites .......... 11 article(s)', aligne sur la largeur."""
    gauche = "  " + texte + " "
    droite = " " + str(valeur)
    return gauche + "." * max(3, L - len(gauche) - len(droite)) + droite


def date_longue(d):
    return "%s %d %s %d" % (JOURS[d.weekday()], d.day, MOIS[d.month - 1], d.year)


# "30-Aug-2026" : la Banque mondiale date ses avis en anglais. On traduit a la
# main, car strptime("%b") depend de la langue du poste.
MOIS_COURTS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun",
     "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_ANGLAISE = re.compile(r"^(\d{1,2})-([A-Za-z]{3})-(\d{4})")


def date_courte(txt):
    if not txt:
        return ""
    for f in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            d = datetime.strptime(txt[:16] if f.endswith("%M") else txt[:10], f)
            return d.strftime("%d/%m/%Y à %H:%M" if f.endswith("%M") else "%d/%m/%Y")
        except ValueError:
            continue
    m = _ANGLAISE.match(txt.strip())
    if m and m.group(2).lower() in MOIS_COURTS:
        return "%02d/%02d/%s" % (int(m.group(1)),
                                 MOIS_COURTS[m.group(2).lower()], m.group(3))
    return txt


def publie_par(origine, date_pub):
    """'Origine — publié le 30/08/2026', sans la mention si la date manque."""
    jolie = date_courte(date_pub)
    return "%s — publié le %s" % (origine, jolie) if jolie else origine


def compte_a_rebours(iso):
    """'dans 12 jour(s)', 'CLÔTURE AUJOURD'HUI', ... a partir d'une date ISO."""
    if not iso:
        return "", None
    try:
        reste = (datetime.strptime(iso, "%Y-%m-%d") - datetime.now()).days + 1
    except ValueError:
        return "", None
    if reste > 0:
        return "dans %d jour(s)" % reste, reste
    if reste == 0:
        return "CLÔTURE AUJOURD'HUI", 0
    return "ÉCHÉANCE DÉPASSÉE", reste


# --------------------------------------------------------------- actualites
def section_actualites(cx, numero, jours, theme=None, maxi=5, tout=False):
    depuis = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d %H:%M")
    sql = ("SELECT theme, titre, resume, source, fiabilite, date_pub, lien "
           "FROM articles WHERE date_pub >= ? ")
    params = [depuis]
    if theme:
        sql += "AND theme = ? "
        params.append(theme)
    sql += "ORDER BY theme, date_pub DESC"
    lignes = cx.execute(sql, params).fetchall()

    out = banniere(numero, "Actualités du jour" if jours <= 1
                   else "Actualités des %d derniers jours" % jours)
    if not lignes:
        out += ["", "    Aucun article sur la période.",
                "    Lancez la collecte : python veille.py --actualites", ""]
        return out, 0, 0

    par_theme = {}
    for ligne in lignes:
        par_theme.setdefault(ligne[0], []).append(ligne)
    ordre = sorted(par_theme, key=lambda t: (t == "Non classé", t))

    n = 0
    for th in ordre:
        groupe = par_theme[th]
        montres = groupe if tout else groupe[:maxi]
        out += sous_titre(th, len(groupe))
        for _, titre, resume, source, fiab, date_pub, lien in montres:
            n += 1
            out.append(entree(n, titre, suffixe="[%s]" % fiab))
            out.append(champ("RÉSUMÉ", (resume or "").strip()
                             or "Pas de résumé fourni par la source."))
            out.append(champ("SOURCE", publie_par(source, date_pub)))
            out.append(champ("LIEN", lien))
            out.append("")
        reste = len(groupe) - len(montres)
        if reste > 0:
            out += ["    (+ %d autre(s) article(s) sur ce domaine — "
                    "rapport complet : --tout)" % reste, ""]
    return out, n, len(lignes)


# --------------------------------------------------------------- appels d'offres
def _fiche_offre(numero, avis):
    """Le pave d'un avis : titre, puis les champs du tableau de bord."""
    (titre, domaine, zone, criteres, budget, limite, origine, lien,
     date_pub, iso) = avis
    rebours, _ = compte_a_rebours(iso)
    out = [entree(numero, titre)]
    out.append(champ("DOMAINE CONCERNÉ", domaine))
    out.append(champ("ZONE DE RÉALISATION", zone))
    out.append(champ("CRITÈRES", criteres))
    out.append(champ("BUDGET D'EXÉCUTION", budget))
    out.append(champ("DATE LIMITE", limite + ("  (%s)" % rebours if rebours else "")))
    out.append(champ("ORIGINE", publie_par(origine, date_pub)))
    out.append(champ("LIEN", lien))
    out.append("")
    return out


def section_offres(cx, numero, garder_expires=False):
    """Les avis regroupes par urgence : l'echeance la plus proche d'abord."""
    lignes = cx.execute(
        "SELECT titre, domaine, zone, criteres, budget, date_limite, origine, "
        "lien, publie_le, limite_iso FROM offres").fetchall()

    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    urgents, ouverts, sans_date, expires = [], [], [], []
    for ligne in lignes:
        iso = ligne[9] or ""
        if not iso:
            sans_date.append(ligne)
        elif iso < aujourdhui:
            expires.append(ligne)
        else:
            _, reste = compte_a_rebours(iso)
            (urgents if reste is not None and reste <= URGENT else ouverts).append(ligne)
    urgents.sort(key=lambda x: x[9])
    ouverts.sort(key=lambda x: x[9])
    expires.sort(key=lambda x: x[9], reverse=True)

    out = banniere(numero, "Appels d'offres et opportunités")
    total = len(urgents) + len(ouverts) + len(sans_date) + \
        (len(expires) if garder_expires else 0)
    if not total:
        out += ["", "    Aucun avis en base.",
                "    Lancez la collecte : python veille.py --offres", ""]
        return out, 0

    out += ["",
            champ("À échéance proche", "%d avis (dans les %d jours)"
                  % (len(urgents), URGENT), 22, 4),
            champ("Encore ouverts", "%d avis" % len(ouverts), 22, 4),
            champ("Sans date annoncée", "%d avis (échéance à vérifier sur l'avis)"
                  % len(sans_date), 22, 4),
            champ("Déjà clos", "%d avis%s" % (len(expires),
                  "" if garder_expires else " (non détaillés — option --expires)"),
                  22, 4)]

    n = 0
    for titre_bloc, lot in (("À échéance proche", urgents),
                            ("Encore ouverts", ouverts),
                            ("Sans date de clôture annoncée", sans_date),
                            ("Déjà clos", expires if garder_expires else [])):
        if not lot:
            continue
        out += sous_titre(titre_bloc, len(lot))
        for avis in lot:
            n += 1
            out += _fiche_offre(n, avis)
    return out, n


# --------------------------------------------------------------- ou chercher
def section_annuaire(numero):
    """Le carnet des guichets : ceux que l'outil releve, et les autres."""
    out = banniere(numero, "Où chercher — le carnet des guichets")
    out += ["",
            champ("Relevés par l'outil", "%d guichet(s) — leurs appels "
                  "remontent dans la section précédente"
                  % len(GUICHETS_RELEVES), 22, 4),
            champ("À consulter à la main", "%d guichet(s) — ils ne publient "
                  "pas de flux lisible" % len(GUICHETS_A_LA_MAIN), 22, 4),
            "",
            "    Repère en fin de ligne : ● relevé automatiquement · "
            "○ à consulter à la main"]

    par_type = {}
    for b in BAILLEURS:
        par_type.setdefault(b["type"], []).append(b)

    for typ in sorted(par_type):
        groupe = sorted(par_type[typ], key=lambda b: b["n"])
        out += sous_titre(typ, len(groupe))
        for b in groupe:
            out.append(entree(b["n"], b["nom"],
                              suffixe="●" if est_releve(b) else "○"))
            out.append(champ("DOMAINES", b["domaines"]))
            out.append(champ("PUBLIC CIBLE", b["cible"]))
            out.append(champ("LIEN", b["lien"]))
            out.append("")
    return out, len(BAILLEURS)


# --------------------------------------------------------------- rapport
def construire(jours=1, theme=None, maxi=5, tout=False, expires=False,
               sections=SECTIONS):
    """Assemble le rapport. `sections` choisit ce qui est produit."""
    if not os.path.exists(DB):
        sys.exit("Base introuvable. Lancez d'abord : python veille.py")
    cx = sqlite3.connect(DB)
    cx.execute("CREATE TABLE IF NOT EXISTS offres (id TEXT PRIMARY KEY, origine TEXT, "
               "titre TEXT, domaine TEXT, zone TEXT, criteres TEXT, budget TEXT, "
               "date_limite TEXT, limite_iso TEXT, publie_le TEXT, lien TEXT, "
               "collecte_le TEXT)")

    maintenant = datetime.now()
    nb_sources = cx.execute("SELECT COUNT(DISTINCT source) FROM articles").fetchone()[0]
    derniere = cx.execute("SELECT MAX(collecte_le) FROM articles").fetchone()[0] or "—"
    nb_guichets = len(GUICHETS_RELEVES)

    corps, sommaire, numero = [], [], 0
    if "actualites" in sections:
        numero += 1
        bloc, n, total = section_actualites(cx, numero, jours, theme, maxi, tout)
        corps += bloc
        compte = ("%d article(s)" % total if n == total
                  else "%d détaillés sur %d" % (n, total))
        sommaire.append(ligne_sommaire("%d. Actualités" % numero, compte))
    if "offres" in sections:
        numero += 1
        bloc, n = section_offres(cx, numero, expires)
        corps += bloc
        sommaire.append(ligne_sommaire("%d. Appels d'offres et opportunités" % numero,
                                       "%d avis" % n))
    if "annuaire" in sections:
        numero += 1
        bloc, n = section_annuaire(numero)
        corps += bloc
        sommaire.append(ligne_sommaire("%d. Où chercher — carnet des guichets" % numero,
                                       "%d guichet(s)" % n))

    tete = titre_encadre([
        "OBSERVATOIRE DE L'ACTUALITÉ GUINÉENNE",
        "RAPPORT DE VEILLE",
        date_longue(maintenant).upper(),
    ])
    tete += [""]
    if "actualites" in sections:
        tete.append(champ("Période couverte", "les %d dernier(s) jour(s)" % jours, 22, 0))
        if theme:
            tete.append(champ("Domaine de suivi", theme, 22, 0))
    tete += [
        champ("Sources suivies", "%d médias guinéens · %d guichets de "
              "financement · Banque mondiale" % (nb_sources, nb_guichets), 22, 0),
        champ("Dernière collecte", derniere, 22, 0),
        champ("Édité le", maintenant.strftime("%d/%m/%Y à %H:%M"), 22, 0),
        "",
        trait("-"),
        "SOMMAIRE",
    ] + sommaire + [trait("-")]

    pied = [
        "",
        trait("="),
        "RAPPEL DE MÉTHODE",
        trait("="),
        "  · Fiabilité A : source utilisable seule. Fiabilité B : à recouper.",
        "    Le repère [A] ou [B] figure en bout de titre de chaque article.",
        "  · Rien n'est diffusé en B ou moins sans deux sources indépendantes,",
        "    c'est-à-dire deux sources qui ne se citent pas l'une l'autre.",
        "  · Vérifier la source, le contenu et le contexte (règle des 3 V) avant",
        "    toute diffusion publique.",
        "  · Domaines, zones, budgets, critères et dates limites sont extraits",
        "    automatiquement : toujours les confirmer sur l'avis original avant",
        "    de préparer un dossier. En cas de doute, l'avis original fait foi.",
        trait("="),
    ]
    cx.close()
    return "\n".join(tete + corps + pied) + "\n"


def main():
    ap = argparse.ArgumentParser(
        description="Rapport de veille — Observatoire de l'actualité guinéenne")
    ap.add_argument("--jours", type=int, default=1,
                    help="période des actualités (défaut : 1)")
    ap.add_argument("--theme", default=None, help="limiter à un domaine de suivi")
    ap.add_argument("--max", type=int, default=5, dest="maxi",
                    help="articles par domaine (défaut : 5)")
    ap.add_argument("--tout", action="store_true", help="ne rien tronquer")
    ap.add_argument("--expires", action="store_true",
                    help="détailler aussi les appels d'offres déjà clos")
    ap.add_argument("--actualites", action="store_true",
                    help="les actualités seules")
    ap.add_argument("--offres", action="store_true",
                    help="les appels d'offres seuls")
    ap.add_argument("--sans-annuaire", action="store_true", dest="sans_annuaire",
                    help="ne pas joindre le carnet des guichets")
    args = ap.parse_args()

    # le suffixe du fichier dit ce qui a ete demande : un rapport partiel
    # n'ecrase donc jamais le rapport complet du jour
    if args.actualites and not args.offres:
        sections, suffixe = ("actualites",), "_actualites"
    elif args.offres and not args.actualites:
        sections, suffixe = ("offres", "annuaire"), "_offres"
    else:
        sections, suffixe = SECTIONS, ""
    if args.sans_annuaire:
        sections = tuple(s for s in sections if s != "annuaire")

    texte = construire(args.jours, args.theme, args.maxi, args.tout,
                       args.expires, sections)

    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, "rapport_%s%s.txt"
                          % (datetime.now().strftime("%Y-%m-%d"), suffixe))
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)

    print(texte)
    print("Rapport enregistré : %s" % chemin)


if __name__ == "__main__":
    main()
