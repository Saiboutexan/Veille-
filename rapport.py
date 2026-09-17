# -*- coding: utf-8 -*-
"""
Genere le rapport de veille en texte : actualites du jour + appels d'offres.

Usage :
    python rapport.py              -> les actualites des dernieres 24 h
    python rapport.py --jours 7    -> la semaine
    python rapport.py --theme "Espace civique"
"""
import argparse
import os
import sqlite3
import sys
import textwrap
from datetime import datetime, timedelta

ICI = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ICI, "veille.db")
DOSSIER = os.path.join(ICI, "rapports")
L = 80                                    # largeur du rapport

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


# --------------------------------------------------------------- mise en forme
def trait(car="="):
    return car * L


def titre_encadre(lignes):
    out = [trait("=")]
    for ligne in lignes:
        out.append(ligne.center(L).rstrip())
    out.append(trait("="))
    return out


def champ(etiquette, valeur, largeur_etiquette=20, indent=4):
    """Une ligne 'ETIQUETTE : valeur' proprement repliee."""
    valeur = " ".join(str(valeur or "—").split())
    tete = " " * indent + etiquette.ljust(largeur_etiquette) + ": "
    creux = " " * len(tete)
    return textwrap.fill(valeur, width=L, initial_indent=tete,
                         subsequent_indent=creux)


def date_longue(d):
    return "%s %d %s %d" % (JOURS[d.weekday()], d.day, MOIS[d.month - 1], d.year)


def date_courte(txt):
    if not txt:
        return "date inconnue"
    for f in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%d-%b-%Y"):
        try:
            d = datetime.strptime(txt[:16] if f.endswith("%M") else txt[:10], f)
            return d.strftime("%d/%m/%Y à %H:%M" if f.endswith("%M") else "%d/%m/%Y")
        except ValueError:
            continue
    return txt


# --------------------------------------------------------------- sections
def section_actualites(cx, jours, theme=None, maxi=5, tout=False):
    depuis = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d %H:%M")
    sql = ("SELECT theme, titre, resume, source, fiabilite, date_pub, lien "
           "FROM articles WHERE date_pub >= ? ")
    params = [depuis]
    if theme:
        sql += "AND theme = ? "
        params.append(theme)
    sql += "ORDER BY theme, date_pub DESC"
    lignes = cx.execute(sql, params).fetchall()

    out = ["", trait("="),
           "1. ACTUALITÉS DU JOUR" if jours <= 1 else "1. ACTUALITÉS DES %d DERNIERS JOURS" % jours,
           trait("=")]
    if not lignes:
        out += ["", "    Aucun article sur la période. Lancez d'abord : python collecte.py", ""]
        return out, 0

    # on regroupe par domaine, "Non classé" en dernier
    par_theme = {}
    for ligne in lignes:
        par_theme.setdefault(ligne[0], []).append(ligne)
    ordre = sorted(par_theme, key=lambda t: (t == "Non classé", t))

    n = 0
    for th in ordre:
        groupe = par_theme[th]
        montres = groupe if tout else groupe[:maxi]
        entete = "--- %s (%d) " % (th.upper(), len(groupe))
        out += ["", entete + "-" * max(0, L - len(entete)), ""]
        for _, titre, resume, source, fiab, date_pub, lien in montres:
            n += 1
            out.append(textwrap.fill("[%d] %s" % (n, titre), width=L,
                                     initial_indent="    ", subsequent_indent="        "))
            out.append(champ("RÉSUMÉ", (resume or "").strip()
                             or "Pas de résumé fourni par la source."))
            out.append(champ("SOURCE", "%s  (fiabilité %s)  —  publié le %s"
                             % (source, fiab, date_courte(date_pub))))
            out.append(champ("LIEN", lien))
            out.append("")
        reste = len(groupe) - len(montres)
        if reste > 0:
            out += ["    (+ %d autre(s) article(s) sur ce domaine — "
                    "rapport complet : --tout)" % reste, ""]
    return out, n


def section_offres(cx, garder_expires=False):
    """Les avis dont l'echeance approche d'abord ; les expires en fin (ou exclus)."""
    lignes = cx.execute(
        "SELECT titre, domaine, zone, criteres, budget, date_limite, origine, lien, "
        "publie_le, limite_iso FROM offres").fetchall()

    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    ouverts, sans_date, expires = [], [], []
    for ligne in lignes:
        iso = ligne[9] or ""
        if not iso:
            sans_date.append(ligne)
        elif iso >= aujourdhui:
            ouverts.append(ligne)
        else:
            expires.append(ligne)
    ouverts.sort(key=lambda x: x[9])            # echeance la plus proche en premier
    retenus = ouverts + sans_date + (expires if garder_expires else [])

    out = ["", trait("="), "2. APPELS D'OFFRES ET OPPORTUNITÉS", trait("=")]
    if not retenus:
        out += ["", "    Aucun avis en cours. Lancez : python offres.py", ""]
        return out, 0

    out += ["", "    %d avis encore ouverts · %d sans date de clôture · %d expirés"
            % (len(ouverts), len(sans_date), len(expires)), ""]

    for i, (titre, domaine, zone, criteres, budget, limite, origine, lien,
            publie, iso) in enumerate(retenus, 1):
        reste = ""
        if iso:
            jours = (datetime.strptime(iso, "%Y-%m-%d") - datetime.now()).days + 1
            reste = ("  (dans %d jour(s))" % jours if jours > 0
                     else "  (CLÔTURE AUJOURD'HUI)" if jours == 0
                     else "  (ÉCHÉANCE DÉPASSÉE)")
        out.append(textwrap.fill("[%d] %s" % (i, titre), width=L,
                                 initial_indent="    ", subsequent_indent="        "))
        out.append(champ("DOMAINE CONCERNÉ", domaine))
        out.append(champ("ZONE DE RÉALISATION", zone))
        out.append(champ("CRITÈRES", criteres))
        out.append(champ("BUDGET D'EXÉCUTION", budget))
        out.append(champ("DATE LIMITE", limite + reste))
        out.append(champ("ORIGINE", "%s  —  publié le %s" % (origine, date_courte(publie))))
        out.append(champ("LIEN", lien))
        out.append("")
    return out, len(retenus)


# --------------------------------------------------------------- rapport
def construire(jours, theme, maxi, tout, expires=False):
    if not os.path.exists(DB):
        sys.exit("Base introuvable. Lancez d'abord : python collecte.py")
    cx = sqlite3.connect(DB)
    cx.execute("CREATE TABLE IF NOT EXISTS offres (id TEXT PRIMARY KEY, origine TEXT, "
               "titre TEXT, domaine TEXT, zone TEXT, criteres TEXT, budget TEXT, "
               "date_limite TEXT, limite_iso TEXT, publie_le TEXT, lien TEXT, "
               "collecte_le TEXT)")

    maintenant = datetime.now()
    nb_sources = cx.execute("SELECT COUNT(DISTINCT source) FROM articles").fetchone()[0]
    derniere = cx.execute("SELECT MAX(collecte_le) FROM articles").fetchone()[0] or "—"

    actus, n_actus = section_actualites(cx, jours, theme, maxi, tout)
    offres, n_offres = section_offres(cx, expires)

    tete = titre_encadre([
        "CONSEIL NATIONAL DES ORGANISATIONS DE LA SOCIÉTÉ CIVILE GUINÉENNE",
        "RAPPORT DE VEILLE",
        date_longue(maintenant).upper(),
    ])
    tete += [
        "",
        champ("Période couverte", "les %d dernier(s) jour(s)" % jours, 22, 0),
        champ("Sources suivies", "%d médias guinéens + Banque mondiale" % nb_sources, 22, 0),
        champ("Dernière collecte", derniere, 22, 0),
        champ("Édité le", maintenant.strftime("%d/%m/%Y à %H:%M"), 22, 0),
        "",
        trait("-"),
        "SOMMAIRE",
        "  1. Actualités du jour %s %3d article(s)" % ("." * 38, n_actus),
        "  2. Appels d'offres et opportunités %s %3d avis" % ("." * 25, n_offres),
        trait("-"),
    ]

    pied = [
        trait("="),
        "RAPPEL DE MÉTHODE",
        trait("="),
        "  · Fiabilité A : source utilisable seule. Fiabilité B : à recouper.",
        "  · Rien ne sort du CNOSCG en B ou moins sans deux sources indépendantes,",
        "    c'est-à-dire deux sources qui ne se citent pas l'une l'autre.",
        "  · Vérifier la source, le contenu et le contexte (règle des 3 V) avant",
        "    toute diffusion publique.",
        "  · Les budgets et critères sont extraits automatiquement : toujours les",
        "    confirmer sur l'avis original via le lien.",
        trait("="),
    ]
    cx.close()
    return "\n".join(tete + actus + offres + pied) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Rapport de veille CNOSCG")
    ap.add_argument("--jours", type=int, default=1, help="période des actualités (défaut : 1)")
    ap.add_argument("--theme", default=None, help="limiter à un domaine de suivi")
    ap.add_argument("--max", type=int, default=5, dest="maxi",
                    help="articles par domaine (défaut : 5)")
    ap.add_argument("--tout", action="store_true", help="ne rien tronquer")
    ap.add_argument("--expires", action="store_true",
                    help="inclure les appels d'offres dont la date est passée")
    args = ap.parse_args()

    texte = construire(args.jours, args.theme, args.maxi, args.tout, args.expires)

    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, "rapport_%s.txt" % datetime.now().strftime("%Y-%m-%d"))
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)

    print(texte)
    print("Rapport enregistré : %s" % chemin)


if __name__ == "__main__":
    main()
