# -*- coding: utf-8 -*-
"""
Tout-en-un : collecte, puis rapport du jour.

On choisit ce que l'on collecte :
    python veille.py                  actualites + appels d'offres
    python veille.py --actualites     les actualites seules
    python veille.py --offres         les appels d'offres seuls
    python veille.py --jours 7        rapport sur la semaine
    python veille.py --sans-rapport   collecter sans editer le rapport
"""
import argparse
import sys

import bailleurs
import collecte
import offres
import rapport


def collecter_actualites():
    """Les articles des medias guineens."""
    collecte.collecter()


def collecter_opportunites():
    """Les appels d'offres : Banque mondiale, presse, puis les bailleurs."""
    offres.collecter_offres()
    print()
    bailleurs.collecter_bailleurs()


def etape(numero, total, titre):
    print()
    print("=" * 70)
    print("ÉTAPE %d/%d — %s" % (numero, total, titre.upper()))
    print("=" * 70)


def main():
    ap = argparse.ArgumentParser(
        description="Observatoire de l'actualité guinéenne")
    ap.add_argument("--actualites", action="store_true",
                    help="collecter les actualités seules")
    ap.add_argument("--offres", action="store_true",
                    help="collecter les appels d'offres seuls")
    ap.add_argument("--jours", type=int, default=1,
                    help="période du rapport (défaut : 1)")
    ap.add_argument("--sans-rapport", action="store_true", dest="sans_rapport",
                    help="collecter sans éditer le rapport")
    args = ap.parse_args()

    # aucune precision = les deux
    faire_actus = args.actualites or not args.offres
    faire_offres = args.offres or not args.actualites

    total = sum([faire_actus, faire_offres]) + (0 if args.sans_rapport else 1)
    numero = 0

    if faire_actus:
        numero += 1
        etape(numero, total, "Actualités")
        collecter_actualites()

    if faire_offres:
        numero += 1
        etape(numero, total, "Appels d'offres")
        collecter_opportunites()

    if args.sans_rapport:
        print("\nCollecte terminée. Rapport : python rapport.py")
        return

    numero += 1
    etape(numero, total, "Rapport")
    argv = ["rapport.py", "--jours", str(args.jours)]
    if faire_actus and not faire_offres:
        argv.append("--actualites")
    elif faire_offres and not faire_actus:
        argv.append("--offres")
    sys.argv = argv
    rapport.main()


if __name__ == "__main__":
    main()
