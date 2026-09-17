# -*- coding: utf-8 -*-
"""
Carnet de sources et grille de codage.

C'est le SEUL fichier a modifier pour adapter la veille :
- ajouter une source  -> une ligne dans SOURCES
- suivre un autre sujet -> un theme et ses mots-cles dans THEMES
"""

# ---------------------------------------------------------------------------
# 1. LE CARNET DE SOURCES
#    fiabilite : "A" = media de reference / source officielle
#                "B" = media etabli, a recouper
#    (voir la grille A-D du module 3 de la formation)
# ---------------------------------------------------------------------------
SOURCES = [
    {"nom": "Guinéenews",       "flux": "https://guineenews.org/feed/",            "fiabilite": "A"},
    {"nom": "Africaguinée",     "flux": "https://www.africaguinee.com/feed/",      "fiabilite": "A"},
    {"nom": "Mediaguinée",      "flux": "https://mediaguinee.com/feed/",           "fiabilite": "B"},
    {"nom": "Guineematin",      "flux": "https://guineematin.com/feed/",           "fiabilite": "A"},
    {"nom": "VisionGuinée",     "flux": "https://www.visionguinee.info/feed/",     "fiabilite": "B"},
    {"nom": "Guinée360",        "flux": "https://www.guinee360.com/feed/",         "fiabilite": "B"},
    {"nom": "Mosaïqueguinée",   "flux": "https://mosaiqueguinee.com/feed/",        "fiabilite": "B"},
    {"nom": "Guinée7",          "flux": "https://www.guinee7.com/feed/",           "fiabilite": "B"},
    {"nom": "Guinée114",        "flux": "https://www.guinee114.com/feed/",         "fiabilite": "B"},
    {"nom": "Kalenews",         "flux": "https://kalenews.org/feed/",              "fiabilite": "B"},
    {"nom": "Le Renifleur 224", "flux": "https://www.lerenifleur224.com/feed/",    "fiabilite": "B"},
    {"nom": "Avenir Guinée",    "flux": "https://www.avenirguinee.org/feed/",      "fiabilite": "B"},
    {"nom": "Investigator",     "flux": "https://investigatorguinee.com/feed/",    "fiabilite": "B"},
    {"nom": "Guinée Live",      "flux": "https://guineelive.com/feed/",            "fiabilite": "B"},
    {"nom": "Conakry Infos",    "flux": "https://conakryinfos.com/feed/",          "fiabilite": "B"},
]

# ---------------------------------------------------------------------------
# 2. LA GRILLE DE CODAGE : les 5 domaines du tableau de bord CNOSCG
#    Un article est range dans le premier theme dont un mot-cle apparait.
#    Les mots sont cherches sans accent, en minuscules, et en MOT ENTIER
#    ("mine" ne declenche pas sur "elimine"). Ecrire simple.
# ---------------------------------------------------------------------------
THEMES = {
    "Espace civique": [
        "hac", "haute autorite de la communication", "liberte de la presse",
        "journaliste", "suspension", "manifestation", "marche pacifique",
        "societe civile", "ong", "activiste", "arrestation", "detention",
        "droits de l'homme", "censure", "accreditation",
    ],
    "Gouvernance et ressources": [
        "mine", "mines", "minier", "miniere", "bauxite", "simandou", "diamant",
        "orpaillage", "extractif",
        "contrat", "marche public", "armp", "budget", "corruption",
        "detournement", "cour des comptes", "transparence", "redevance",
    ],
    "Cohésion sociale": [
        "conflit", "tension", "violence", "affrontement", "communautaire",
        "foncier", "litige", "mediation", "dialogue", "paix", "discours de haine",
        "exécutif communal", "executif communal", "maire", "commune",
    ],
    "Services publics": [
        "electricite", "edg", "coupure", "eau", "seg", "hopital", "sante",
        "greve", "ecole", "enseignant", "universite", "route", "transport",
        "carburant", "inondation",
    ],
    "Violences basées sur le genre": [
        "vbg", "viol", "excision", "mgf", "mariage precoce", "mariage force",
        "violence conjugale", "violences faites aux femmes", "harcelement",
    ],
    "Électoral": [
        "election", "electoral", "scrutin", "vote", "urne", "candidat",
        "campagne electorale", "referendum", "legislative", "legislatives",
        "communale", "communales", "dgel", "bulletin de vote",
    ],
}

AUTRE = "Non classé"


# ---------------------------------------------------------------------------
# 3. APPELS D'OFFRES — ce qui fait qu'un article est un avis
# ---------------------------------------------------------------------------
MOTS_AVIS = [
    "appel d'offres", "appel a offres", "avis d'appel", "avis de recrutement",
    "manifestation d'interet", "termes de reference", "appel a candidatures",
    "appel a projets", "appel a propositions", "avis de consultation",
    "sollicitation de prix", "avis de marche", "avis de selection",
    "recrutement d'un consultant", "avis de vacance",
]

# ---------------------------------------------------------------------------
# 4. DOMAINE CONCERNE par un avis (premier domaine dont un mot apparait)
# ---------------------------------------------------------------------------
DOMAINES = {
    "Gouvernance et société civile": [
        "gouvernance", "societe civile", "renforcement de capacites", "plaidoyer",
        "redevabilite", "transparence", "citoyen", "democratie", "decentralisation",
        "etat civil", "justice", "droits humains", "paix", "cohesion",
    ],
    "Santé": ["sante", "hopital", "medical", "nutrition", "vaccination",
              "paludisme", "vih", "epidemie", "medicament", "clinique"],
    "Éducation et formation": ["education", "ecole", "enseignement", "formation",
                               "universite", "alphabetisation", "scolaire", "eleves"],
    "Agriculture et élevage": ["agricole", "agriculture", "elevage", "peche",
                               "semence", "riz", "cultures", "rural", "irrigation"],
    "Eau et assainissement": ["eau", "assainissement", "forage", "hygiene",
                              "latrine", "adduction", "potable"],
    "Énergie et électricité": ["energie", "electricite", "electrification",
                               "solaire", "reseau electrique", "centrale"],
    "Infrastructures et travaux": ["travaux", "route", "pont", "batiment",
                                   "construction", "rehabilitation", "amenagement",
                                   "genie civil", "piste"],
    "Mines et environnement": ["mine", "minier", "miniere", "bauxite", "environnement",
                               "environnemental", "social", "reinstallation", "foret"],
    "Numérique et données": ["informatique", "numerique", "logiciel", "systeme d'information",
                             "donnees", "digital", "plateforme", "internet"],
    "Genre et protection sociale": ["genre", "femmes", "vbg", "protection sociale",
                                    "enfants", "jeunes", "inclusion", "handicap"],
    "Finance, audit et conseil": ["audit", "comptable", "comptabilite", "financier",
                                  "fiscal", "juridique", "expert", "consultant",
                                  "assistance technique", "etude", "evaluation"],
}

# ---------------------------------------------------------------------------
# 5. ZONE DE REALISATION — regions et prefectures de Guinee
# ---------------------------------------------------------------------------
LIEUX_GUINEE = [
    # regions administratives
    "Conakry", "Boké", "Kindia", "Mamou", "Labé", "Faranah", "Kankan", "Nzérékoré",
    "N'Zérékoré",
    # prefectures
    "Boffa", "Fria", "Gaoual", "Koundara", "Coyah", "Dubréka", "Forécariah",
    "Télimélé", "Dalaba", "Pita", "Koubia", "Lélouma", "Mali", "Tougué",
    "Dabola", "Dinguiraye", "Kissidougou", "Kérouané", "Kouroussa", "Mandiana",
    "Siguiri", "Beyla", "Guéckédou", "Lola", "Macenta", "Yomou",
    # communes de Conakry
    "Kaloum", "Dixinn", "Matam", "Ratoma", "Matoto",
]
