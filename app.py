# -*- coding: utf-8 -*-
"""
Application web : produit et affiche le rapport de veille du CNOSCG.

Local  :  streamlit run app.py
En ligne : https://share.streamlit.io  (dépôt Saiboutexan/Veille-)

L'application ne fait pas de tableau de bord : elle sert le rapport texte,
le même que celui produit par `python rapport.py`.
"""
import io
import os
import sqlite3
from contextlib import redirect_stdout
from datetime import datetime

import streamlit as st

import collecte
import offres
import rapport

ICI = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ICI, "veille.db")

st.set_page_config(page_title="Veille CNOSCG", page_icon="📰", layout="centered")


# ------------------------------------------------------------------ outils
def compter():
    """(articles, avis, date de la dernière collecte)."""
    if not os.path.exists(DB):
        return 0, 0, None
    with sqlite3.connect(DB) as cx:
        try:
            n_art = cx.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
            derniere = cx.execute("SELECT MAX(collecte_le) FROM articles").fetchone()[0]
        except sqlite3.OperationalError:
            n_art, derniere = 0, None
        try:
            n_off = cx.execute("SELECT COUNT(*) FROM offres").fetchone()[0]
        except sqlite3.OperationalError:
            n_off = 0
    return n_art, n_off, derniere


def lancer_collecte():
    """Collecte actualités + appels d'offres, en affichant la progression."""
    journal = io.StringIO()
    barre = st.progress(0, text="Lecture des flux des médias guinéens…")
    try:
        with redirect_stdout(journal):
            collecte.collecter()
        barre.progress(50, text="Recherche des appels d'offres…")
        with redirect_stdout(journal):
            offres.collecter_offres()
        barre.progress(100, text="Terminé.")
    except Exception as e:
        barre.empty()
        st.error("La collecte a échoué : %s" % e)
        return journal.getvalue()
    barre.empty()
    return journal.getvalue()


# ------------------------------------------------------------------ en-tête
st.title("Veille CNOSCG")
st.caption("Conseil National des Organisations de la Société Civile Guinéenne — "
           "actualités guinéennes et appels d'offres")

n_art, n_off, derniere = compter()

# Sur Streamlit Cloud le disque est réinitialisé à chaque redémarrage :
# si la base est vide, on collecte une première fois automatiquement.
if n_art == 0:
    st.info("Première ouverture : constitution de la base. Cela prend une minute.")
    with st.spinner("Collecte en cours…"):
        journal = lancer_collecte()
    n_art, n_off, derniere = compter()
    with st.expander("Détail de la collecte"):
        st.code(journal or "—")

# ------------------------------------------------------------------ options
with st.sidebar:
    st.header("Le rapport")
    jours = st.slider("Période (jours)", 1, 30, 1,
                      help="1 = les actualités des dernières 24 heures")
    maxi = st.slider("Articles par domaine", 1, 30, 5)
    tout = st.checkbox("Ne rien tronquer")
    expires = st.checkbox("Inclure les appels d'offres clos")

    themes = ["Tous les domaines"]
    if os.path.exists(DB):
        with sqlite3.connect(DB) as cx:
            try:
                themes += [t[0] for t in cx.execute(
                    "SELECT DISTINCT theme FROM articles ORDER BY theme")]
            except sqlite3.OperationalError:
                pass
    choix = st.selectbox("Domaine de suivi", themes)
    theme = None if choix == "Tous les domaines" else choix

    st.divider()
    st.metric("Articles en base", n_art)
    st.metric("Appels d'offres", n_off)
    st.caption("Dernière collecte : %s" % (derniere or "—"))

    if st.button("Actualiser la collecte", use_container_width=True, type="primary"):
        with st.spinner("Collecte en cours…"):
            journal = lancer_collecte()
        st.session_state["journal"] = journal
        st.rerun()

if "journal" in st.session_state:
    with st.expander("Détail de la dernière collecte"):
        st.code(st.session_state.pop("journal") or "—")

# ------------------------------------------------------------------ rapport
if n_art == 0:
    st.warning("Aucun article en base. Utilisez « Actualiser la collecte ».")
    st.stop()

texte = rapport.construire(jours, theme, maxi, tout, expires)

st.download_button(
    "Télécharger le rapport (.txt)",
    texte.encode("utf-8"),
    file_name="rapport_veille_%s.txt" % datetime.now().strftime("%Y-%m-%d"),
    mime="text/plain",
    use_container_width=True,
)

# monospace à largeur fixe : la mise en page 80 colonnes du rapport est conservée
st.code(texte, language=None)
