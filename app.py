# -*- coding: utf-8 -*-
"""
Application web : collecte, consulte et telecharge la veille du CNOSCG.

Local  :  streamlit run app.py
En ligne : https://share.streamlit.io  (depot Saiboutexan/Veille-)

Quatre onglets : les appels d'offres, les actualites, le carnet des guichets
et le rapport texte. Le rapport et le classeur Excel se telechargent depuis
la barre laterale, qui commande aussi ce que l'on collecte.
"""
import io
import os
import sqlite3
from contextlib import redirect_stdout
from datetime import datetime, timedelta

import streamlit as st

import bailleurs
import collecte
import export
import offres
import rapport
from sources import BAILLEURS, est_releve

ICI = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ICI, "veille.db")

st.set_page_config(page_title="Veille CNOSCG", page_icon="📰", layout="wide")

VERT = "#0b4f3a"

st.markdown("""
<style>
  .bandeau      { background:%s; color:#fff; padding:1.1rem 1.4rem;
                  border-radius:.5rem; margin-bottom:1.2rem; }
  .bandeau h1   { color:#fff; font-size:1.45rem; margin:0; line-height:1.3; }
  .bandeau p    { color:#d7e8e1; font-size:.86rem; margin:.35rem 0 0; }
  .fiche        { border:1px solid #e3e6e3; border-left:4px solid #c9cec9;
                  border-radius:.4rem; padding:.85rem 1.05rem; margin-bottom:.7rem; }
  .fiche.urgent { border-left-color:#c62828; }
  .fiche.ouvert { border-left-color:#2e7d32; }
  .fiche.floue  { border-left-color:#ef9a2f; }
  .fiche.clos   { border-left-color:#9e9e9e; opacity:.66; }
  .fiche h4     { margin:0 0 .5rem; font-size:1rem; line-height:1.38; }
  .etiq         { display:inline-block; font-size:.7rem; font-weight:600;
                  padding:.13rem .5rem; border-radius:.8rem; margin-right:.3rem; }
  .e-urgent     { background:#fce4e4; color:#9b1c1c; }
  .e-ouvert     { background:#e6f4ea; color:#1b5e20; }
  .e-floue      { background:#fff2cc; color:#8a5a00; }
  .e-clos       { background:#eeeeee; color:#555; }
  .e-dom        { background:#eef2f7; color:#33475b; }
  .meta         { font-size:.82rem; color:#4a534d; line-height:1.55; }
  .meta b       { color:#222c26; }
</style>
""" % VERT, unsafe_allow_html=True)


# ------------------------------------------------------------------ outils
def compter():
    """(articles, avis, date de la derniere collecte)."""
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


def lancer_collecte(quoi="tout"):
    """Collecte ce qui est demande : "actualites", "offres" ou "tout"."""
    journal = io.StringIO()
    etapes = []
    if quoi in ("tout", "actualites"):
        etapes.append(("Lecture des flux des médias guinéens…", collecte.collecter))
    if quoi in ("tout", "offres"):
        etapes.append(("Appels d'offres : Banque mondiale et presse…",
                       offres.collecter_offres))
        etapes.append(("Opportunités des bailleurs et de l'Atlas des OSC…",
                       bailleurs.collecter_bailleurs))

    barre = st.progress(0, text=etapes[0][0])
    try:
        for i, (libelle, faire) in enumerate(etapes):
            barre.progress(int(100 * i / len(etapes)), text=libelle)
            with redirect_stdout(journal):
                faire()
        barre.progress(100, text="Terminé.")
    except Exception as e:
        barre.empty()
        st.error("La collecte a échoué : %s" % e)
        return journal.getvalue()
    barre.empty()
    return journal.getvalue()


@st.cache_data(show_spinner=False)
def texte_rapport(jours, theme, maxi, tout, expires, jeton):
    """Le rapport texte. `jeton` = date de la derniere collecte : il suffit a
    invalider le cache des qu'on a collecte du neuf."""
    return rapport.construire(jours, theme, maxi, tout, expires)


@st.cache_data(show_spinner=False)
def classeur(jours, jeton):
    """Le classeur Excel, construit une seule fois par jeu de reglages."""
    return export.octets(jours)


def etat_avis(iso):
    """(classe CSS, etiquette) selon l'echeance."""
    rebours, reste = rapport.compte_a_rebours(iso)
    if reste is None:
        return "floue", "Échéance à vérifier"
    if reste < 0:
        return "clos", "Clos — %s" % rebours
    if reste == 0:
        return "urgent", "Clôture aujourd'hui"
    if reste <= rapport.URGENT:
        return "urgent", "Échéance proche — %s" % rebours
    return "ouvert", "Ouvert — %s" % rebours


def echappe(txt):
    return (str(txt or "—").replace("&", "&amp;")
            .replace("<", "&lt;").replace(">", "&gt;"))


# ------------------------------------------------------------------ en-tete
st.markdown(
    '<div class="bandeau"><h1>Veille CNOSCG</h1><p>Conseil National des '
    'Organisations de la Société Civile Guinéenne — actualités guinéennes, '
    "appels d'offres et opportunités de financement</p></div>",
    unsafe_allow_html=True)

n_art, n_off, derniere = compter()

# Sur Streamlit Cloud le disque est reinitialise a chaque redemarrage :
# si la base est vide, on collecte une premiere fois automatiquement.
if n_art == 0:
    st.info("Première ouverture : constitution de la base. Cela prend une minute.")
    with st.spinner("Collecte en cours…"):
        journal = lancer_collecte("tout")
    n_art, n_off, derniere = compter()
    with st.expander("Détail de la collecte"):
        st.code(journal or "—")

# ------------------------------------------------------------------ reglages
with st.sidebar:
    st.header("Collecter")
    quoi = st.radio(
        "Que faut-il relever ?",
        ["Tout", "Les actualités seules", "Les appels d'offres seuls"],
        help="Les appels d'offres couvrent la Banque mondiale, la presse "
             "guinéenne et les guichets de financement du carnet.")
    cle = {"Tout": "tout", "Les actualités seules": "actualites",
           "Les appels d'offres seuls": "offres"}[quoi]

    if st.button("Lancer la collecte", use_container_width=True, type="primary"):
        with st.spinner("Collecte en cours…"):
            st.session_state["journal"] = lancer_collecte(cle)
        st.rerun()

    st.caption("Dernière collecte : %s" % (derniere or "—"))
    st.divider()

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
    st.header("Télécharger")
    jour = datetime.now().strftime("%Y-%m-%d")
    if n_art:
        st.download_button(
            "Rapport complet (.txt)",
            texte_rapport(jours, theme, maxi, tout, expires,
                          derniere).encode("utf-8"),
            file_name="rapport_veille_%s.txt" % jour,
            mime="text/plain", use_container_width=True)
        st.download_button(
            "Classeur à trier (.xlsx)", classeur(jours, derniere),
            file_name="veille_%s.xlsx" % jour,
            mime="application/vnd.openxmlformats-officedocument."
                 "spreadsheetml.sheet",
            use_container_width=True)

    st.divider()
    st.metric("Articles en base", n_art)
    st.metric("Appels d'offres", n_off)

if "journal" in st.session_state:
    with st.expander("Détail de la dernière collecte"):
        st.code(st.session_state.pop("journal") or "—")

if n_art == 0:
    st.warning("Aucun article en base. Utilisez « Lancer la collecte ».")
    st.stop()

# ------------------------------------------------------------------ onglets
onglet_offres, onglet_actus, onglet_carnet, onglet_texte = st.tabs(
    ["Appels d'offres", "Actualités", "Carnet des guichets", "Rapport texte"])

cx = sqlite3.connect(DB)

# ---------------------------------------------------------- appels d'offres
with onglet_offres:
    lignes = cx.execute(
        "SELECT titre, domaine, zone, criteres, budget, date_limite, origine, "
        "lien, publie_le, limite_iso FROM offres").fetchall()

    def rang(l):
        _, reste = rapport.compte_a_rebours(l[9])
        if reste is None:
            return (1, 0)
        return (0, reste) if reste >= 0 else (2, -reste)
    lignes.sort(key=rang)

    etats = [etat_avis(l[9])[0] for l in lignes]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("À échéance proche", etats.count("urgent"))
    c2.metric("Encore ouverts", etats.count("ouvert"))
    c3.metric("Échéance à vérifier", etats.count("floue"))
    c4.metric("Déjà clos", etats.count("clos"))

    domaines = sorted({l[1] for l in lignes if l[1]})
    gauche, droite = st.columns([3, 2])
    filtre_dom = gauche.multiselect("Filtrer par domaine", domaines,
                                    placeholder="Tous les domaines")
    masquer_clos = droite.checkbox("Masquer les avis clos", value=not expires)

    montres = [l for l in lignes
               if (not filtre_dom or l[1] in filtre_dom)
               and not (masquer_clos and etat_avis(l[9])[0] == "clos")]
    st.caption("%d avis affiché(s) sur %d en base" % (len(montres), len(lignes)))

    for (titre, domaine, zone, criteres, budget, limite, origine, lien,
         publie, iso) in montres:
        classe, etiquette = etat_avis(iso)
        st.markdown(
            '<div class="fiche %s">'
            '<h4>%s</h4>'
            '<span class="etiq e-%s">%s</span>'
            '<span class="etiq e-dom">%s</span>'
            '<div class="meta" style="margin-top:.55rem">'
            '<b>Date limite :</b> %s &nbsp;·&nbsp; <b>Zone :</b> %s<br>'
            '<b>Budget :</b> %s<br>'
            '<b>Critères :</b> %s<br>'
            '<b>Origine :</b> %s</div></div>'
            % (classe, echappe(titre), classe, echappe(etiquette),
               echappe(domaine), echappe(limite), echappe(zone),
               echappe(budget), echappe(criteres),
               echappe(rapport.publie_par(origine, publie))),
            unsafe_allow_html=True)
        st.link_button("Ouvrir l'avis", lien)

# ---------------------------------------------------------------- actualites
with onglet_actus:
    depuis = datetime.now() - timedelta(days=jours)
    sql = ("SELECT theme, titre, resume, source, fiabilite, date_pub, lien "
           "FROM articles WHERE date_pub >= ? ")
    params = [depuis.strftime("%Y-%m-%d %H:%M")]
    if theme:
        sql += "AND theme = ? "
        params.append(theme)
    arts = cx.execute(sql + "ORDER BY theme, date_pub DESC", params).fetchall()

    st.caption("%d article(s) sur les %d dernier(s) jour(s)" % (len(arts), jours))
    if not arts:
        st.info("Aucun article sur la période. Élargissez la période à gauche, "
                "ou lancez une collecte.")

    par_theme = {}
    for a in arts:
        par_theme.setdefault(a[0], []).append(a)

    for th in sorted(par_theme, key=lambda t: (t == "Non classé", t)):
        groupe = par_theme[th]
        with st.expander("%s — %d article(s)" % (th, len(groupe)),
                         expanded=len(par_theme) <= 2):
            for _, titre, resume, source, fiab, date_pub, lien in (
                    groupe if tout else groupe[:maxi]):
                st.markdown(
                    '<div class="fiche"><h4>%s</h4>'
                    '<span class="etiq e-dom">Fiabilité %s</span>'
                    '<div class="meta" style="margin-top:.5rem">%s<br>'
                    '<b>%s</b> — %s</div></div>'
                    % (echappe(titre), echappe(fiab),
                       echappe(resume or "Pas de résumé fourni par la source."),
                       echappe(source), echappe(rapport.date_courte(date_pub)
                                                or "date inconnue")),
                    unsafe_allow_html=True)
                st.link_button("Lire l'article", lien)
            reste = len(groupe) - len(groupe if tout else groupe[:maxi])
            if reste:
                st.caption("+ %d autre(s) — cochez « Ne rien tronquer » à gauche."
                           % reste)

# ------------------------------------------------------------------ carnet
with onglet_carnet:
    releves = [b for b in BAILLEURS if est_releve(b)]
    st.caption("%d guichets au carnet : %d relevés par l'outil, %d à consulter "
               "à la main." % (len(BAILLEURS), len(releves),
                               len(BAILLEURS) - len(releves)))
    filtre = st.multiselect("Filtrer par type",
                            sorted({b["type"] for b in BAILLEURS}),
                            placeholder="Tous les types")
    st.dataframe(
        [{"N°": b["n"], "Organisme / plateforme": b["nom"], "Type": b["type"],
          "Relevé": "● oui" if est_releve(b) else "○ à la main",
          "Domaines / opportunités": b["domaines"],
          "Public cible": b["cible"], "Lien officiel": b["lien"]}
         for b in BAILLEURS if not filtre or b["type"] in filtre],
        use_container_width=True, hide_index=True,
        column_config={"Lien officiel": st.column_config.LinkColumn(
            "Lien officiel", display_text="Ouvrir")})

# ------------------------------------------------------------- rapport texte
with onglet_texte:
    st.caption("Le rapport tel qu'il sort de « python veille.py » — "
               "à copier dans un mail ou à imprimer.")
    st.code(texte_rapport(jours, theme, maxi, tout, expires, derniere),
            language=None)

cx.close()
