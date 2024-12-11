# INF_8810 Projet 2

## Partie 1: Données

### 1. Origine des données
### 2. Contexte du jeu de données
### 3. Prétraitement

## Partie 2: Chargement dans Neo4j

### 1. Données à charger sur Neo4j
* recipes.csv
* reviews.csv

Les deux fichiers .csv sont téléchargés et sauvegardés localement dans le repertoire d'importation par défaut de Neo4j à partir du téléchargement du dossier compressé sur Kaggle. 

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

.recipes.csv

.sampled_recipes.csv

```
load csv with headers from 'file:///sampled_recipes.csv' as row 
merge (r:Recipe {recipe_id: tointeger(row.id)})
set r.recipe_name =  COALESCE(row.name, "Not Available"),
    r.minutes = tointeger(row.minutes),
    r.date = date(row.submitted),
    r.description = row.description,
    r.n_steps = tointeger(row.n_steps)

with r,row
unwind split(row.tags, ',') as tag
merge (t:Tag {tag_name: trim(tag)})
merge (r)-[:HAS_TAG]->(t)

with r,row
unwind split(row.ingredients, ',') as ingredient
merge (i:Ingredient {ingredient_name: trim(ingredient)})
merge (r)-[:HAS_INGREDIENT]->(i)
```
- Charger les données de `reviews.csv`

.reviews.csv

.filtered_reviews.csv à partir de sample_recipes.csv

```
load csv with headers from 'file:///filtered_reviews.csv' as row
merge (u:User {user_id: tointeger(row.user_id)})
with u, row
match (r:Recipe {recipe_id: TOINTEGER(row.recipe_id)})
merge (u)-[lien:REVIEWED]->(r)

set lien.rating = tointeger(row.rating),
    lien.review_date = date(row.date),
    lien.review = row.review
```

## 