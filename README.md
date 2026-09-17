# Veille CNOSCG — rapport d'actualités et d'appels d'offres

Petit outil qui produit chaque jour **un rapport texte** sur la Guinée :

1. **Actualités du jour** — titre, information résumée, source
2. **Appels d'offres** — domaine, zone, critères, budget, date limite, lien

Aucun serveur, aucune interface : un fichier `.txt` que l'on lit, imprime,
copie dans un mail ou envoie sur WhatsApp.

---

## Lancer

Double-cliquez sur **`lancer.bat`**, ou en ligne de commande :

```bash
python veille.py
```

Cela enchaîne les trois étapes et écrit le rapport dans
`rapports/rapport_AAAA-MM-JJ.txt`.

Chaque étape peut aussi se lancer seule :

```bash
python collecte.py      # 1. actualités des 15 médias  -> veille.db
python offres.py        # 2. appels d'offres            -> veille.db
python rapport.py       # 3. génère le rapport texte
```

### Options du rapport

```bash
python rapport.py --jours 7                  # la semaine au lieu du jour
python rapport.py --max 10                   # 10 articles par domaine (défaut : 5)
python rapport.py --tout                     # ne rien tronquer
python rapport.py --theme "Espace civique"   # un seul domaine
python rapport.py --expires                  # inclure les avis déjà clos
```

---

## Ce que ça collecte

**Actualités — 15 médias guinéens** (flux RSS) : Guinéenews, Africaguinée,
Mediaguinée, Guineematin, VisionGuinée, Guinée360, Mosaïqueguinée, Guinée7,
Guinée114, Kalenews, Le Renifleur 224, Avenir Guinée, Investigator,
Guinée Live, Conakry Infos.

Chaque article est rangé dans un **domaine de suivi** : Espace civique,
Gouvernance et ressources, Cohésion sociale, Services publics, VBG, Électoral.
Les sources sont notées **A** (utilisable seule) ou **B** (à recouper).

**Appels d'offres — deux origines :**

| Origine | Ce qu'elle apporte |
|---|---|
| Banque mondiale (API publique) | Avis structurés concernant la Guinée : intitulé, pays, date de clôture, texte complet. Les marchés déjà attribués (*Contract Award*) sont écartés. |
| Presse guinéenne | Les avis publiés dans les articles déjà collectés (appel d'offres, manifestation d'intérêt, TDR, appel à candidatures…). |

Pour chaque avis, l'outil déduit du texte : le **domaine**, la **zone**
(préfectures et communes guinéennes citées), les **critères**, le **budget**
s'il est mentionné, et la **date limite**. Les avis sont triés par échéance,
la plus proche en premier, avec un compte à rebours.

> Ces champs sont extraits automatiquement : **toujours les confirmer sur
> l'avis original** via le lien avant de préparer un dossier.

---

## Adapter l'outil

Tout se règle dans **`sources.py`**, sans toucher au reste :

| Pour… | Modifier |
|---|---|
| ajouter un média | une ligne dans `SOURCES` |
| suivre un nouveau sujet | un thème dans `THEMES` |
| affiner un domaine d'appel d'offres | `DOMAINES` |
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

**ReliefWeb** et **UNGM** exigent une clé ou un compte approuvé : à demander
au nom du CNOSCG pour élargir la couverture ONG.

---

## Fichiers

```
veille/
├── veille.py      tout-en-un (collecte + offres + rapport)
├── lancer.bat     double-clic sous Windows
├── sources.py     LE fichier à adapter : sources, thèmes, domaines, lieux
├── collecte.py    actualités  -> veille.db
├── offres.py      appels d'offres -> veille.db
├── rapport.py     génère le rapport texte
├── veille.db      base SQLite (créée automatiquement)
└── rapports/      les rapports produits, un par jour
```

Dépendances : `requests` uniquement (le reste est dans la bibliothèque
standard de Python).

---

## Méthode de veille

Le rapport rappelle en pied de page les règles du module de formation :

- fiabilité **A** = utilisable seule, **B** = à recouper ;
- rien ne sort du CNOSCG en B ou moins **sans deux sources indépendantes**,
  c'est-à-dire deux sources qui ne se citent pas l'une l'autre ;
- vérifier **la source, le contenu et le contexte** (règle des 3 V) avant
  toute diffusion publique.
