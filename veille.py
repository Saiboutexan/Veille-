# -*- coding: utf-8 -*-
"""
Tout-en-un : collecte les actualites, collecte les appels d'offres,
puis genere le rapport du jour.

Usage :  python veille.py
         python veille.py --jours 7        (rapport sur la semaine)
"""
import sys

import collecte
import offres
import rapport


def main():
    jours = 1
    if "--jours" in sys.argv:
        try:
            jours = int(sys.argv[sys.argv.index("--jours") + 1])
        except (IndexError, ValueError):
            sys.exit("Usage : python veille.py --jours 7")

    print("=" * 70)
    print("ETAPE 1/3 — ACTUALITES")
    print("=" * 70)
    collecte.collecter()

    print()
    print("=" * 70)
    print("ETAPE 2/3 — APPELS D'OFFRES")
    print("=" * 70)
    offres.collecter_offres()

    print()
    print("=" * 70)
    print("ETAPE 3/3 — RAPPORT")
    print("=" * 70)
    sys.argv = ["rapport.py", "--jours", str(jours)]
    rapport.main()


if __name__ == "__main__":
    main()
