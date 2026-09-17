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


# ---------------------------------------------------------------------------
# 6. LE CARNET DES BAILLEURS ET PLATEFORMES D'OPPORTUNITES
#    Base "appels et projets - societe civile 2026" : 27 guichets ou paraissent
#    les appels a projets, financements, bourses et marches ouverts aux OSC.
#
#      "flux"       flux RSS lisible automatiquement (None = a consulter a la main)
#      "collecteur" collecteur dedie ecrit dans bailleurs.py (ex. "atlas")
#
#    Les guichets SANS flux ne sont pas perdus : ils sortent dans la section
#    "Ou chercher" du rapport, avec leur domaine, leur public cible et leur
#    lien. Le jour ou l'un d'eux publie un flux, il suffit de renseigner
#    "flux" ici : le reste du programme le prend en compte tout seul.
# ---------------------------------------------------------------------------
BAILLEURS = [
    {"n": 1, "nom": 'Atlas des OSC de Guinée',
     "type": 'Veille nationale',
     "domaines": 'Appels à projets, financements, formations, bourses',
     "cible": 'OSC guinéennes',
     "lien": 'https://atlasdesoscgn.com/',
     "flux": None, "collecteur": 'atlas'},
    {"n": 2, "nom": 'AFD – Appels à projets',
     "type": 'Bailleur',
     "domaines": 'Initiatives OSC, gouvernance, climat, biodiversité, égalité, éducation',
     "cible": 'OSC éligibles selon appel',
     "lien": 'https://www.afd.fr/fr/appels-a-projets/liste',
     "flux": 'https://www.afd.fr/rss.xml'},
    {"n": 3, "nom": 'AFD – Initiatives OSC',
     "type": 'Bailleur',
     "domaines": 'Financement de projets OSC / ODD / solidarité internationale',
     "cible": 'OSC françaises et OSC de droit local sous conditions',
     "lien": 'https://www.afd.fr/fr/osc-francaises',
     "flux": None, "couvert_par": 2},
    {"n": 4, "nom": 'Union européenne – Guinée',
     "type": 'Bailleur',
     "domaines": 'Société civile, droits humains, gouvernance, démocratie',
     "cible": 'OSC selon appel',
     "lien": 'https://www.eeas.europa.eu/delegations/guinea_fr',
     "flux": None},
    {"n": 5, "nom": 'PNUD Guinée',
     "type": 'ONU / bailleur',
     "domaines": 'Gouvernance, environnement, développement, inclusion',
     "cible": 'ONG / OCB selon programme',
     "lien": 'https://www.undp.org/fr/guinea',
     "flux": None},
    {"n": 6, "nom": 'FEM / GEF – PMF',
     "type": 'Bailleur',
     "domaines": 'Environnement, biodiversité, climat, communautés',
     "cible": 'ONG et organisations communautaires',
     "lien": 'https://www.undp.org/fr/guinea',
     "flux": None},
    {"n": 7, "nom": 'Expertise France',
     "type": 'Agence de développement',
     "domaines": 'Gouvernance, santé, migration, développement, société civile',
     "cible": 'ONG / OSC selon appel',
     "lien": 'https://www.expertisefrance.fr/',
     "flux": 'https://www.expertisefrance.fr/rss.xml'},
    {"n": 8, "nom": 'ONU Femmes',
     "type": 'ONU / bailleur',
     "domaines": 'Égalité femmes-hommes, autonomisation, lutte contre les violences',
     "cible": 'OSC selon appel',
     "lien": 'https://africa.unwomen.org/fr/where-we-are/west-and-central-africa/guinea',
     "flux": 'https://africa.unwomen.org/rss.xml'},
    {"n": 9, "nom": 'UNICEF Guinée',
     "type": 'ONU / bailleur',
     "domaines": 'Enfance, protection, éducation, jeunesse',
     "cible": 'ONG / partenaires selon appel',
     "lien": 'https://www.unicef.org/guinea/',
     "flux": None},
    {"n": 10, "nom": 'UNFPA Guinée',
     "type": 'ONU / bailleur',
     "domaines": 'Jeunesse, santé, égalité, population',
     "cible": 'OSC / partenaires selon appel',
     "lien": 'https://guinea.unfpa.org/',
     "flux": 'https://guinea.unfpa.org/rss.xml'},
    {"n": 11, "nom": 'OIM Guinée',
     "type": 'ONU / bailleur',
     "domaines": 'Migration, mobilité, réintégration',
     "cible": 'OSC / partenaires selon appel',
     "lien": 'https://www.iom.int/countries/guinea',
     "flux": None},
    {"n": 12, "nom": 'Ambassade de France en Guinée',
     "type": 'Coopération',
     "domaines": 'Société civile, droits humains, gouvernance, culture',
     "cible": 'OSC selon dispositif',
     "lien": 'https://gn.ambafrance.org/',
     "flux": None},
    {"n": 13, "nom": 'Fondation Orange Guinée',
     "type": 'Fondation',
     "domaines": 'Éducation, inclusion numérique, femmes, entrepreneuriat',
     "cible": 'ONG / associations selon appel',
     "lien": 'https://www.orange-guinee.com/',
     "flux": None},
    {"n": 14, "nom": 'CEPF',
     "type": 'Fonds environnemental',
     "domaines": 'Biodiversité, conservation, communautés',
     "cible": 'ONG / OSC locales selon appel',
     "lien": 'https://www.cepf.net/',
     "flux": None},
    {"n": 15, "nom": 'NED – National Endowment for Democracy',
     "type": 'Fondation',
     "domaines": 'Démocratie, droits humains, gouvernance, société civile',
     "cible": 'ONG / OSC',
     "lien": 'https://www.ned.org/',
     "flux": 'https://www.ned.org/feed/'},
    {"n": 16, "nom": 'Open Society Foundations',
     "type": 'Fondation',
     "domaines": 'Justice, droits, gouvernance, société civile',
     "cible": 'OSC selon programme',
     "lien": 'https://www.opensocietyfoundations.org/',
     "flux": None},
    {"n": 17, "nom": 'Fondation Ford',
     "type": 'Fondation',
     "domaines": 'Justice sociale, droits, égalité, gouvernance',
     "cible": 'Organisations éligibles selon programme',
     "lien": 'https://www.fordfoundation.org/',
     "flux": 'https://www.fordfoundation.org/feed/'},
    {"n": 18, "nom": 'OSIWA',
     "type": 'Fondation / Afrique',
     "domaines": 'Gouvernance, démocratie, droits, société civile',
     "cible": 'OSC africaines selon appel',
     "lien": 'https://www.osiwa.org/',
     "flux": None},
    {"n": 19, "nom": "African Women's Development Fund",
     "type": 'Fondation',
     "domaines": 'Droits et leadership des femmes',
     "cible": 'Organisations féministes africaines',
     "lien": 'https://awdf.org/',
     "flux": 'https://awdf.org/feed/'},
    {"n": 20, "nom": 'Global Greengrants Fund',
     "type": 'Fondation',
     "domaines": 'Climat, environnement, justice environnementale',
     "cible": 'Groupes communautaires / OSC',
     "lien": 'https://www.greengrants.org/',
     "flux": 'https://www.greengrants.org/feed/'},
    {"n": 21, "nom": 'Rufford Foundation',
     "type": 'Fondation',
     "domaines": 'Conservation, biodiversité',
     "cible": 'ONG / chercheurs / conservation',
     "lien": 'https://www.rufford.org/',
     "flux": None},
    {"n": 22, "nom": 'UNGM – United Nations Global Marketplace',
     "type": 'ONU',
     "domaines": "Appels d'offres, achats, contrats ONU",
     "cible": 'Entreprises / ONG selon avis',
     "lien": 'https://www.ungm.org/',
     "flux": None},
    {"n": 23, "nom": 'Devex',
     "type": 'Plateforme',
     "domaines": 'Opportunités de développement, appels, contrats, emplois',
     "cible": 'Professionnels / organisations',
     "lien": 'https://www.devex.com/',
     "flux": None},
    {"n": 24, "nom": 'ReliefWeb',
     "type": 'ONU / veille',
     "domaines": 'Humanitaire, appels, financements, opportunités',
     "cible": 'ONG / acteurs humanitaires',
     "lien": 'https://reliefweb.int/',
     "flux": None},
    {"n": 25, "nom": 'Funds for NGOs',
     "type": 'Plateforme de veille',
     "domaines": 'Subventions et appels internationaux pour ONG',
     "cible": 'ONG / OSC',
     "lien": 'https://fundsforngos.org/',
     "flux": 'https://fundsforngos.org/feed/'},
    {"n": 26, "nom": 'Ministère des Affaires étrangères – Guinée / SABATY',
     "type": 'Programme national',
     "domaines": 'Développement local, diaspora, initiatives locales',
     "cible": 'Associations de la diaspora + structures locales',
     "lien": 'https://mae.gov.gn/projet-sabaty-soutien-aux-initiatives-de-la-diaspora-guineenne-pour-le-developpement-local-durable/',
     "flux": 'https://mae.gov.gn/feed/'},
    {"n": 27, "nom": 'INSPIRED Guinée / Ouvrir Les Horizons',
     "type": 'Programme société civile',
     "domaines": 'Dialogue régional, participation citoyenne, gouvernance locale',
     "cible": 'OSC guinéennes',
     "lien": 'https://atlasdesoscgn.com/opportunites/cadres-de-dialogue-regionaux-et-forums-regionaux-multi-acteurs-0wXNd',
     "flux": None},
]

# ---------------------------------------------------------------------------
# 7. CE QUI FAIT QU'UNE PUBLICATION DE BAILLEUR EST UNE OPPORTUNITE
#    Les flux des bailleurs melangent communiques, rapports et appels. On ne
#    retient que les entrees qui portent un de ces mots. Beaucoup de ces
#    bailleurs publient en anglais : les deux langues sont donc couvertes.
# ---------------------------------------------------------------------------
MOTS_OPPORTUNITE = MOTS_AVIS + [
    # francais
    "appel a proposition", "avis a manifestation", "appel a manifestation",
    "avis de recrutement", "subvention", "financement de projets",
    "fonds d'appui", "guichet", "bourse d'etudes", "appel a candidature",
    "date limite de depot", "dossier de candidature",
    # anglais
    "call for proposals", "call for proposal", "call for applications",
    "call for application", "request for proposals", "request for expression",
    "expression of interest", "funding opportunity", "funding opportunities",
    "grant opportunity", "grants program", "grant program", "open call",
    "apply now", "applications are open", "call for tenders", "invitation to bid",
    "fellowship", "scholarship", "deadline for applications",
]


def est_releve(guichet):
    """Vrai si l'outil releve ce guichet tout seul : soit il a un flux, soit
    un collecteur dedie, soit un autre guichet du carnet publie sur le meme
    site (cle "couvert_par")."""
    return bool(guichet.get("flux") or guichet.get("collecteur")
                or guichet.get("couvert_par"))


GUICHETS_RELEVES = [b for b in BAILLEURS if est_releve(b)]
GUICHETS_A_LA_MAIN = [b for b in BAILLEURS if not est_releve(b)]
