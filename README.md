# Veille CNOSCG — actualités, appels d'offres et opportunités de financement

Outil qui produit chaque jour, sur la Guinée :

1. **Actualités du jour** — titre, information résumée, source
2. **Appels d'offres et opportunités** — domaine, zone, critères, budget,
   date limite, lien
3. **Où chercher** — le carnet des 27 guichets de financement ouverts aux OSC

Trois façons de s'en servir : en ligne de commande, dans l'application web, ou
en récupérant le **classeur Excel** pour trier et filtrer.

---

## Lancer

### En ligne de commande

Double-cliquez sur **`lancer.bat`**, ou :

```bash
python veille.py
```

Cela collecte tout et écrit le rapport dans `rapports/rapport_AAAA-MM-JJ.txt`.

**On choisit ce que l'on collecte :**

```bash
python veille.py --actualites      # les actualités seules
python veille.py --offres          # les appels d'offres seuls
python veille.py --jours 7         # rapport sur la semaine
python veille.py --sans-rapport    # collecter sans éditer le rapport
```

Chaque étape peut aussi se lancer seule :

```bash
python collecte.py      # actualités des 28 médias      -> veille.db
python offres.py        # Banque mondiale + presse      -> veille.db
python bailleurs.py     # les guichets du carnet        -> veille.db
python rapport.py       # génère le rapport texte
python export.py        # génère le classeur Excel
```

### Application web

```bash
pip install -r requirements.txt
streamlit run app.py
```

Quatre onglets : **Appels d'offres** (fiches colorées par urgence, filtrables
par domaine), **Actualités** (regroupées par domaine de suivi), **Carnet des
guichets** (les 27 organismes, triables), **Rapport texte** (le rapport tel
qu'il sort en ligne de commande).

La barre latérale permet de choisir ce que l'on collecte, de régler la période
et le domaine, puis de télécharger le rapport `.txt` ou le classeur `.xlsx`.

### Options du rapport

```bash
python rapport.py --jours 7                  # la semaine au lieu du jour
python rapport.py --max 10                   # 10 articles par domaine (défaut : 5)
python rapport.py --tout                     # ne rien tronquer
python rapport.py --theme "Espace civique"   # un seul domaine
python rapport.py --expires                  # détailler les avis déjà clos
python rapport.py --actualites               # les actualités seules
python rapport.py --offres                   # les appels d'offres seuls
python rapport.py --sans-annuaire            # sans le carnet des guichets
```

### Classeur Excel

```bash
python export.py            # rapports/veille_AAAA-MM-JJ.xlsx
python export.py --jours 7
```

Trois feuilles, en-têtes figées et filtres automatiques :

| Feuille | Contenu |
|---|---|
| Appels d'offres | un avis par ligne, l'échéance la plus proche en haut, état en couleur (clos / clôture aujourd'hui / échéance proche / ouvert) |
| Actualités | un article par ligne, avec domaine, source et fiabilité |
| Carnet des guichets | les 27 organismes, avec la mention de ceux que l'outil relève seul |

---

## Ce que ça collecte

**Actualités — 28 médias guinéens** dont les flux ont été testés un par un :

| Catégorie | Médias |
|---|---|
| Agence de presse | AGP |
| Généralistes de référence | Guinéenews, Africaguinée, Guineematin |
| Radio / TV | Espace FM |
| Généralistes | Mediaguinée, VisionGuinée, Guinée360, Guinée7, Guinée114, Mosaïqueguinée, Laguinee.info, Le Courrier de Conakry, Avenir Guinée, Le Révélateur 224, Kalenews, Guinée Lumière, ActuConakry, GuinéeTime, GuinéeDirect, Focus Guinée, Conakrylemag, Le Renifleur 224, Investigator, Guinée Live, Conakry Infos |
| Spécialisés | Guinée Mines Nature, Gnakrylive |

Chaque article est rangé dans un **domaine de suivi** : Espace civique,
Gouvernance et ressources, Cohésion sociale, Services publics, VBG, Électoral.
Les sources sont notées **A** (utilisable seule) ou **B** (à recouper).

Une vingtaine d'autres médias guinéens n'exposent **pas** de flux RSS
exploitable (Le Djely, RTG, Djoma Média, FIM FM, Le Lynx, Horoya…). Ils sont
listés en commentaire à la fin de `sources.py` : ils restent à surveiller
manuellement, et se rebranchent en une ligne si un flux apparaît.

**Appels d'offres et opportunités — trois origines :**

| Origine | Ce qu'elle apporte |
|---|---|
| Banque mondiale (API publique) | Avis structurés concernant la Guinée : intitulé, pays, date de clôture, texte complet. Les marchés déjà attribués (*Contract Award*) sont écartés. |
| Presse guinéenne | Les avis publiés dans les articles déjà collectés (appel d'offres, manifestation d'intérêt, TDR, appel à candidatures…). |
| Carnet des bailleurs | Les appels à projets, financements et bourses publiés par les guichets ouverts aux OSC guinéennes. |

### Le carnet des bailleurs — 27 guichets, dont 12 relevés seuls

Le carnet vient de la base *« appels et projets — société civile 2026 »*. Il
est dans `sources.py`, sous `BAILLEURS`. Chaque guichet porte son type, ses
domaines, son public cible et son lien officiel.

**12 sont relevés automatiquement :**

| Guichet | Comment |
|---|---|
| Atlas des OSC de Guinée | pas de flux RSS, mais son plan de site expose la rubrique *Opportunités* : chaque fiche est lue directement |
| AFD (appels à projets · initiatives OSC) | flux RSS, les deux entrées partageant le même site |
| Expertise France, ONU Femmes, UNFPA Guinée | flux RSS |
| NED, Fondation Ford, AWDF, Global Greengrants | flux RSS |
| Funds for NGOs, MAE Guinée / SABATY | flux RSS |

Ces flux mêlent communiqués, rapports et appels : seules les publications qui
portent un mot de `MOTS_OPPORTUNITE` sont retenues (les deux langues sont
couvertes, beaucoup de ces bailleurs publiant en anglais).

**15 sont à consulter à la main** — PNUD, Union européenne, UNICEF, OIM, UNGM,
Devex, ReliefWeb, OSIWA, CEPF, Open Society, Rufford, Fondation Orange,
Ambassade de France, FEM/GEF, INSPIRED Guinée : ils ne publient pas de flux
lisible, ou refusent les requêtes automatiques. Ils ne sont pas perdus pour
autant : ils figurent tous dans la section **« Où chercher »** du rapport et
dans la feuille *Carnet* du classeur, avec domaines, public cible et lien.

Le jour où l'un d'eux publie un flux, il suffit de renseigner sa clé `"flux"`
dans `sources.py` : le reste du programme le prend en compte tout seul.

Pour chaque avis, l'outil déduit du texte : le **domaine**, la **zone**, les
**critères**, le **budget** s'il est mentionné, et la **date limite**. Les avis
sont triés par échéance, la plus proche en premier, avec un compte à rebours.

> Ces champs sont extraits automatiquement : **toujours les confirmer sur
> l'avis original** via le lien avant de préparer un dossier. Quand aucune
> échéance n'est annoncée, l'outil écrit « Voir l'avis » plutôt que de
> risquer une date fausse.

---

## Adapter l'outil

Tout se règle dans **`sources.py`**, sans toucher au reste :

| Pour… | Modifier |
|---|---|
| ajouter un média | une ligne dans `SOURCES` |
| ajouter un bailleur ou une plateforme | une ligne dans `BAILLEURS` |
| brancher un guichet qui vient d'ouvrir un flux | sa clé `"flux"` dans `BAILLEURS` |
| suivre un nouveau sujet | un thème dans `THEMES` |
| affiner un domaine d'appel d'offres | `DOMAINES` |
| élargir ce qui compte comme opportunité | `MOTS_OPPORTUNITE` |
| ajouter une localité | `LIEUX_GUINEE` |

Après modification des mots-clés, réappliquez le classement à la base :

```bash
python collecte.py --reclasser
```

Les mots-clés sont cherchés **sans accent et en mot entier** : `mine` ne se
déclenche pas sur « élimine ».

---

## Sources non incluses, et pourquoi

Les portails publics guinéens (**ARMP**, **DNMP**, `marchespublics.gov.gn`)
n'ont pas répondu depuis le poste où l'outil a été monté. S'ils sont
joignables depuis la Guinée, ce sont les sources les plus pertinentes :
ajoutez-les dans `SOURCES` s'ils publient un flux RSS, sinon dans `offres.py`
sur le modèle de la fonction `banque_mondiale()`.

**ReliefWeb** : l'API v1 a été fermée, et la v2 refuse les requêtes sans compte
approuvé (`appname` enregistré). **UNGM** et **Devex** exigent eux aussi un
compte. À demander au nom du CNOSCG pour élargir la couverture ONG — d'ici là,
les trois restent dans le carnet, à consulter à la main.

---

## Déploiement sur Streamlit Community Cloud

1. Aller sur **https://share.streamlit.io** et se connecter avec GitHub.
2. *Create app* → *Deploy a public app from GitHub*.
3. Renseigner :
   - **Repository** : `Saiboutexan/Veille-`
   - **Branch** : `main`
   - **Main file path** : `app.py`
4. *Deploy*. La première ouverture constitue la base (environ une minute).

**À savoir sur l'hébergement gratuit :** le disque est réinitialisé à chaque
redémarrage de l'application. La base `veille.db` n'est donc pas conservée —
c'est voulu : l'application la reconstruit automatiquement à la première
ouverture, et le bouton « Lancer la collecte » la met à jour. L'historique
long terme se conserve en local, en lançant `python veille.py` sur un poste.

---

## Fichiers

```
veille/
├── app.py            application web (Streamlit), quatre onglets
├── veille.py         tout-en-un (collecte au choix + rapport)
├── lancer.bat        double-clic sous Windows
├── sources.py        LE fichier à adapter : médias, bailleurs, thèmes, domaines
├── collecte.py       actualités                      -> veille.db
├── offres.py         Banque mondiale + presse        -> veille.db
├── bailleurs.py      les 27 guichets du carnet       -> veille.db
├── rapport.py        génère le rapport texte
├── export.py         génère le classeur Excel
├── requirements.txt  dépendances pour le déploiement
├── veille.db         base SQLite (créée automatiquement, non versionnée)
└── rapports/         rapports et classeurs produits (non versionnés)
```

Dépendances : `requests` pour la collecte, `streamlit` pour l'application web,
`openpyxl` pour le classeur Excel. Le reste vient de la bibliothèque standard.

---

## Méthode de veille

Le rapport rappelle en pied de page les règles du module de formation :

- fiabilité **A** = utilisable seule, **B** = à recouper ;
- rien ne sort du CNOSCG en B ou moins **sans deux sources indépendantes**,
  c'est-à-dire deux sources qui ne se citent pas l'une l'autre ;
- vérifier **la source, le contenu et le contexte** (règle des 3 V) avant
  toute diffusion publique.
