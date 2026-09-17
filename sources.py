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
    # --- agence de presse nationale -----------------------------------------
    {"nom": "AGP",                   "fiabilite": "A", "categorie": "Agence de presse",
     "flux": "https://agpguinee.com/feed/"},

    # --- generalistes de reference ------------------------------------------
    {"nom": "Guinéenews",            "fiabilite": "A", "categorie": "Actualités générales",
     "flux": "https://guineenews.org/feed/"},
    {"nom": "Africaguinée",          "fiabilite": "A", "categorie": "Actualités générales",
     "flux": "https://www.africaguinee.com/feed/"},
    {"nom": "Guineematin",           "fiabilite": "A", "categorie": "Actualités générales",
     "flux": "https://guineematin.com/feed/"},

    # --- radio / television --------------------------------------------------
    {"nom": "Espace FM",             "fiabilite": "A", "categorie": "Radio / TV",
     "flux": "https://espacefmguinee.info/feed/"},

    # --- generalistes --------------------------------------------------------
    {"nom": "Mediaguinée",           "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://mediaguinee.com/feed/"},
    {"nom": "VisionGuinée",          "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://www.visionguinee.info/feed/"},
    {"nom": "Guinée360",             "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://www.guinee360.com/feed/"},
    {"nom": "Guinée7",               "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://www.guinee7.com/feed/"},
    {"nom": "Guinée114",             "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://www.guinee114.com/feed/"},
    {"nom": "Mosaïqueguinée",        "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://mosaiqueguinee.com/feed/"},
    {"nom": "Laguinee.info",         "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://laguinee.info/feed/"},
    {"nom": "Le Courrier de Conakry", "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://lecourrierdeconakry.com/feed/"},
    {"nom": "Avenir Guinée",         "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://www.avenirguinee.org/feed/"},
    {"nom": "Le Révélateur 224",     "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://lerevelateur224.com/feed/"},
    {"nom": "Kalenews",              "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://kalenews.org/feed/"},
    {"nom": "Guinée Lumière",        "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://guineelumiere.com/feed/"},
    {"nom": "ActuConakry",           "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://actuconakry.com/feed/"},
    {"nom": "GuinéeTime",            "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://guineetime.com/feed/"},
    {"nom": "GuinéeDirect",          "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://guineedirect.org/feed/"},
    {"nom": "Focus Guinée",          "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://focusguinee.info/feed/"},
    {"nom": "Conakrylemag",          "fiabilite": "B", "categorie": "Actualités / société",
     "flux": "https://conakrylemag.com/feed/"},
    {"nom": "Le Renifleur 224",      "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://www.lerenifleur224.com/feed/"},
    {"nom": "Investigator",          "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://investigatorguinee.com/feed/"},
    {"nom": "Guinée Live",           "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://guineelive.com/feed/"},
    {"nom": "Conakry Infos",         "fiabilite": "B", "categorie": "Actualités générales",
     "flux": "https://conakryinfos.com/feed/"},

    # --- specialises ---------------------------------------------------------
    {"nom": "Guinée Mines Nature",   "fiabilite": "B", "categorie": "Mines / environnement",
     "flux": "https://guineeminesnature.com/feed/"},
    {"nom": "Gnakrylive",            "fiabilite": "B", "categorie": "Culture / événements",
     "flux": "https://gnakrylive.com/?format=feed&type=rss"},
]

# Medias guineens SANS flux RSS exploitable (testes le 17/09/2026).
# A surveiller a la main, ou a rebrancher si un flux apparait :
#   Le Djely (403), Inquisiteur, Sitanews, Generation224, Agriguinee,
#   GuineePlus, Conakrylive, Hadafo Medias  -> pas de flux
#   Oeil224, Guinee Eco, GuineeInfos, RTG, Djoma Media, CIS Medias,
#   Gangan RTV, FIM FM                      -> site injoignable au test
# Sans site web dans la liste de depart : Guinee Actuelle, Sabari FM,
#   Radio Kankan, Le Lynx, Le Populaire, Le Diplomate, L'Independant,
#   Horoya, Emergence Magazine, Objectif 224, Le Factuel de Guinee.

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
