# INF8810 Projet 2

## Partie 1: Données

### 1. Origine des données
### 2. Contexte du jeu de données
### 3. Prétraitement
- raw_recipes.csv
- raw_reviews.csv

Les deux fichiers .csv sont téléchargés et sauvegardés localement dans le repertoire d'importation par défaut de Neo4j à partir du dossier compressé téléchargé sur Kaggle.

- Exécuter `pretraitement.py` avec les chemins des fichiers selon votre repertoire

## Partie 2: Chargement dans Neo4j

### 1. Données à charger sur Neo4j
* recipes.csv
* reviews.csv



### 2. Traitements/modifications lors du chargement
### 3. Chargement des données utilisant Neo4j

#### Configuration avec Neo4j Desktop
- Les fichiers `recipes.csv` et `reviews.csv` doivent être dans le repertoire d"importation de Neo4j.
- <i>Start</i> un projet sur Neo4j Desktop et ouvrir avec une fenêtre Neo4j.

- Réinitialiser la base de données
```
match(n)
detach delete n
```
- Charger les données de `recipes.csv`


```
load csv with headers from 'file:///recipes.csv' as row 
merge (r:Recipe {recipe_id: tointeger(row.id)})
set r.recipe_name =  COALESCE(row.name, "Not Available"),
    r.minutes = tointeger(row.minutes),
    r.date = date(row.submitted),
    r.description = row.description,
    r.n_steps = tointeger(row.n_steps)

with r,row
unwind split(row.ingredients, ',') as ingredient
merge (i:Ingredient {ingredient_name: trim(ingredient)})
merge (r)-[:HAS_INGREDIENT]->(i)
```

Note: j'ai enlever les noeuds Tag pour l'instant (entre merge noeuds Recipe et merge Ingredient)
```
with r,row
unwind split(row.tags, ',') as tag
merge (t:Tag {tag_name: trim(tag)})
merge (r)-[:HAS_TAG]->(t)
```

- Charger les données de `reviews.csv`

```
load csv with headers from 'file:///reviews.csv' as row
merge (u:User {user_id: tointeger(row.user_id)})
with u, row
match (r:Recipe {recipe_id: TOINTEGER(row.recipe_id)})
merge (u)-[lien:REVIEWED]->(r)

set lien.rating = tointeger(row.rating),
    lien.review_date = date(row.date),
    lien.review = row.review
```

## 