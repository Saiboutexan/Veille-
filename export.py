# -*- coding: utf-8 -*-
"""
Export Excel de la veille : un classeur de trois feuilles, pret a trier
et a filtrer.

    1. Appels d'offres   un avis par ligne, echeance la plus proche en haut
    2. Actualites        un article par ligne
    3. Carnet            les 27 guichets du carnet BAILLEURS

Usage :
    python export.py                  -> veille_AAAA-MM-JJ.xlsx
    python export.py --jours 7
    python export.py --fichier C:\\chemin\\veille.xlsx
"""
import argparse
import io
import os
import sqlite3
from datetime import datetime, timedelta

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from rapport import date_courte
from sources import BAILLEURS, est_releve

ICI = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ICI, "veille.db")
URGENT = 15                       # en deca, une echeance est "proche"

# couleurs : un vert sobre pour les en-tetes, un feu tricolore discret
# pour les echeances
VERT = "0B4F3A"
BLANC = "FFFFFF"
GRIS = "F2F2F2"
ROUGE_CLAIR = "FCE4E4"
ORANGE_CLAIR = "FFF2CC"
VERT_CLAIR = "E6F4EA"

BORDURE = Border(*[Side(style="thin", color="D9D9D9")] * 4)


def _entetes(ws, colonnes):
    """Ecrit la ligne d'en-tete, la fige et pose le filtre automatique."""
    ws.append([c[0] for c in colonnes])
    for i, (intitule, largeur) in enumerate(colonnes, 1):
        cel = ws.cell(row=1, column=i)
        cel.font = Font(bold=True, color=BLANC, size=11)
        cel.fill = PatternFill("solid", fgColor=VERT)
        cel.alignment = Alignment(vertical="center", horizontal="center",
                                  wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = largeur
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"


def _finir(ws, nb_colonnes, alterner=True):
    """Bordures, alignement haut, et une ligne sur deux grisee."""
    for ligne in range(2, ws.max_row + 1):
        for col in range(1, nb_colonnes + 1):
            cel = ws.cell(row=ligne, column=col)
            cel.alignment = Alignment(vertical="top", wrap_text=True)
            cel.border = BORDURE
            if alterner and ligne % 2 == 0:
                cel.fill = PatternFill("solid", fgColor=GRIS)
    if ws.max_row > 1:
        ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(nb_colonnes), ws.max_row)


def _jours_restants(iso):
    if not iso:
        return None
    try:
        return (datetime.strptime(iso, "%Y-%m-%d") - datetime.now()).days + 1
    except ValueError:
        return None


def _etat(reste):
    if reste is None:
        return "Date à vérifier", None
    if reste < 0:
        return "Clos", ROUGE_CLAIR
    if reste == 0:
        return "Clôture aujourd'hui", ROUGE_CLAIR
    if reste <= URGENT:
        return "Échéance proche", ORANGE_CLAIR
    return "Ouvert", VERT_CLAIR


# --------------------------------------------------------------- feuilles
def feuille_offres(wb, cx):
    ws = wb.create_sheet("Appels d'offres")
    _entetes(ws, [("État", 18), ("Jours restants", 11), ("Date limite", 14),
                  ("Intitulé de l'avis", 58), ("Domaine", 26), ("Zone", 24),
                  ("Budget", 20), ("Critères", 60), ("Origine", 32),
                  ("Publié le", 13), ("Lien", 46)])

    lignes = cx.execute(
        "SELECT titre, domaine, zone, criteres, budget, date_limite, origine, "
        "lien, publie_le, limite_iso FROM offres").fetchall()

    # ouverts d'abord, du plus urgent au moins urgent ; sans date ensuite ;
    # clos en dernier
    def rang(l):
        reste = _jours_restants(l[9])
        if reste is None:
            return (1, 0)
        return (0, reste) if reste >= 0 else (2, -reste)
    lignes.sort(key=rang)

    for (titre, domaine, zone, criteres, budget, limite, origine, lien,
         publie, iso) in lignes:
        reste = _jours_restants(iso)
        etat, couleur = _etat(reste)
        ws.append([etat, reste if reste is not None else "", limite, titre,
                   domaine, zone, budget, criteres, origine,
                   date_courte(publie), lien])
        if couleur:
            cel = ws.cell(row=ws.max_row, column=1)
            cel.fill = PatternFill("solid", fgColor=couleur)
            cel.font = Font(bold=True)
        lien_cel = ws.cell(row=ws.max_row, column=11)
        if lien:
            lien_cel.hyperlink = lien
            lien_cel.font = Font(color="0563C1", underline="single")

    _finir(ws, 11, alterner=False)
    return ws.max_row - 1


def feuille_actualites(wb, cx, jours):
    ws = wb.create_sheet("Actualités")
    _entetes(ws, [("Domaine de suivi", 26), ("Titre", 62), ("Résumé", 72),
                  ("Source", 22), ("Fiabilité", 10), ("Publié le", 17),
                  ("Lien", 46)])

    depuis = (datetime.now() - timedelta(days=jours)).strftime("%Y-%m-%d %H:%M")
    for theme, titre, resume, source, fiab, date_pub, lien in cx.execute(
            "SELECT theme, titre, resume, source, fiabilite, date_pub, lien "
            "FROM articles WHERE date_pub >= ? ORDER BY theme, date_pub DESC",
            (depuis,)):
        ws.append([theme, titre, resume or "", source, fiab,
                   date_courte(date_pub), lien])
        cel = ws.cell(row=ws.max_row, column=7)
        if lien:
            cel.hyperlink = lien
            cel.font = Font(color="0563C1", underline="single")
        ws.cell(row=ws.max_row, column=5).alignment = Alignment(
            horizontal="center", vertical="top")

    _finir(ws, 7)
    return ws.max_row - 1


def feuille_carnet(wb):
    ws = wb.create_sheet("Carnet des guichets")
    _entetes(ws, [("N°", 6), ("Organisme / plateforme", 44), ("Type", 26),
                  ("Domaines / opportunités", 58), ("Public cible", 40),
                  ("Relevé par l'outil", 16), ("Lien officiel", 52)])

    for b in BAILLEURS:
        releve = est_releve(b)
        ws.append([b["n"], b["nom"], b["type"], b["domaines"], b["cible"],
                   "Oui" if releve else "À consulter à la main", b["lien"]])
        cel = ws.cell(row=ws.max_row, column=6)
        cel.fill = PatternFill("solid",
                               fgColor=VERT_CLAIR if releve else ORANGE_CLAIR)
        cel.alignment = Alignment(horizontal="center", vertical="top",
                                  wrap_text=True)
        lien_cel = ws.cell(row=ws.max_row, column=7)
        if b["lien"]:
            lien_cel.hyperlink = b["lien"]
            lien_cel.font = Font(color="0563C1", underline="single")

    _finir(ws, 7, alterner=False)
    return ws.max_row - 1


# --------------------------------------------------------------- classeur
def classeur(jours=1):
    """Monte le classeur en memoire et renvoie (workbook, comptes)."""
    if not os.path.exists(DB):
        raise SystemExit("Base introuvable. Lancez d'abord : python veille.py")
    cx = sqlite3.connect(DB)
    cx.execute("CREATE TABLE IF NOT EXISTS offres (id TEXT PRIMARY KEY, origine TEXT, "
               "titre TEXT, domaine TEXT, zone TEXT, criteres TEXT, budget TEXT, "
               "date_limite TEXT, limite_iso TEXT, publie_le TEXT, lien TEXT, "
               "collecte_le TEXT)")

    wb = Workbook()
    wb.remove(wb.active)                       # la feuille vide par defaut
    comptes = {
        "offres": feuille_offres(wb, cx),
        "actualites": feuille_actualites(wb, cx, jours),
        "carnet": feuille_carnet(wb),
    }
    cx.close()

    wb.properties.title = "Observatoire de l'actualité guinéenne"
    wb.properties.creator = "Observatoire de l'actualité guinéenne"
    return wb, comptes


def construire(jours=1, chemin=None):
    """Enregistre le classeur sur le disque et renvoie (chemin, comptes)."""
    wb, comptes = classeur(jours)
    if chemin is None:
        chemin = os.path.join(ICI, "rapports", "veille_%s.xlsx"
                              % datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(os.path.dirname(chemin) or ".", exist_ok=True)
    wb.save(chemin)
    return chemin, comptes


def octets(jours=1):
    """Le classeur en memoire, pour le bouton de telechargement de l'app."""
    tampon = io.BytesIO()
    classeur(jours)[0].save(tampon)
    return tampon.getvalue()


def main():
    ap = argparse.ArgumentParser(
        description="Export Excel — Observatoire de l'actualité guinéenne")
    ap.add_argument("--jours", type=int, default=1,
                    help="période des actualités exportées (défaut : 1)")
    ap.add_argument("--fichier", default=None, help="chemin du classeur à écrire")
    args = ap.parse_args()

    chemin, comptes = construire(args.jours, args.fichier)
    print("Classeur enregistré : %s" % chemin)
    print("  Appels d'offres     : %3d ligne(s)" % comptes["offres"])
    print("  Actualités          : %3d ligne(s)" % comptes["actualites"])
    print("  Carnet des guichets : %3d ligne(s)" % comptes["carnet"])


if __name__ == "__main__":
    main()
