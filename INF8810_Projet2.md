# INF8810 Projet 2

## Partie 1: Données

### 1. Origine des données


https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions

### 2. Contexte du jeu de données
### 3. Prétraitement
- RAW_recipes.csv
- RAW_interactions.csv

Les deux fichiers .csv sont téléchargés et sauvegardés localement dans le repertoire d'importation par défaut de Neo4j à partir du dossier compressé téléchargé sur Kaggle.

- Exécuter `pretraitement.py` avec le chemin de votre repertoire d'importantion Neo4j

## Partie 2: Chargement dans Neo4j

### 1. Données à charger sur Neo4j
* recipes.csv
* interactions.csv



### 2. Traitements/modifications lors du chargement
### 3. Chargement des données utilisant Neo4j

#### Configuration avec Neo4j Desktop
- Les fichiers `recipes.csv` et `interactions.csv` doivent être dans le repertoire d"importation de Neo4j.
- <i>Start</i> un projet sur Neo4j Desktop et ouvrir avec une fenêtre Neo4j.

- Réinitialiser la base de données
```
match(n)
detach delete n
```
- Charger les données de `recipes.csv`

Pour 5000 recettes échantillonées dans recipes.csv, voici le nombre de noeuds et liens créés:
> Added 9241 labels, created 9241 nodes, set 39241 properties, created 45652 relationships, completed after 88940 ms.

```
load csv with headers from 'file:///recipes.csv' as row 
merge (r:Recipe {recipe_id: tointeger(row.id)})
set r.recipe_name =  COALESCE(row.name, "Not Available"),
    r.minutes = tointeger(row.minutes),
    r.date = date(row.submitted),
    r.description = row.description,
    r.n_steps = tointeger(row.n_steps),
    r.tags = case when row.tags IS NOT NULL then split (row.tags, '|')
                else []
                end

with r,row
unwind split(row.ingredients, '|') as ingredient
merge (i:Ingredient {ingredient_name: trim(ingredient)})
merge (r)-[:HAS_INGREDIENT]->(i)
```


- Charger les données de `interactions.csv`

Suite au chargement de ces données, les noeuds et liens suivants ont été ajoutés:
> Added 12288 labels, created 12288 nodes, set 84195 properties, created 23969 relationships, completed after 249342 ms.

```
load csv with headers from 'file:///interactions.csv' as row
merge (u:User {user_id: tointeger(row.user_id)})
with u, row
match (r:Recipe {recipe_id: TOINTEGER(row.recipe_id)})
merge (u)-[lien:REVIEWED]->(r)

set lien.rating = tointeger(row.rating)
```

## Partie 3: Recommandation

### 1. Recommandation proposée
*qu'est-ceq qui est recoomandé, à qui faites vous cette recommandation.
decreivez en detail approche e votre requête et code dans rapport*

### 2. Requête pour faire une recommandation

#### 1. Approche filtrage collaboratif
```
match (p1:User {user_id: 1072593})-[x:REVIEWED]->(r:Recipe)<-[y:REVIEWED]-(p2:User)
with p1, p2, r,
    sum(x.rating * y.rating) as xyDotProduct,
    sqrt(reduce(xDot = 0.0, a in collect(x.rating) | xDot + a^2)) as xLength,
    sqrt(reduce(yDot = 0.0, b in collect(y.rating) | yDot + b^2)) as yLength
where xLength > 0 and yLength > 0
with p1, p2, xyDotProduct / (xLength * yLength) as sim
order by sim desc

match (p2)-[:REVIEWED]->(rec:Recipe)
where not (p1)-[:REVIEWED]->(rec)
return rec.recipe_name as recommandation,rec.description as description, sim as cosinusScore
limit 5

```

Cette approche fonctionne s'il y a assez de recettes communément évaluées par notre utilisateur d'intérêt `p1` et d'autres utilisateurs `p2`. Dans le cas où il n'y a pas assez d'évaluations, on peut utiliser une approche basée contenu. Cette approche est donnée ci-dessous et expliquée dans la section "3. Approche de la requête de recommandation et le code > 2. Approche basée contenu

#### 2. Approche basée contenu
```
match (u:User {user_id: 1072593})-[:REVIEWED]->(r:Recipe)
with u, collect(r) AS reviewedRecipes

match (r1:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)<-[:HAS_INGREDIENT]-(r2:Recipe)
where r1 in reviewedRecipes and r1 <> r2

with u, r1, r2,
    count(i) as commonIngredients,
    abs(r1.minutes - r2.minutes) as diffMin,
    abs(r1.n_steps - r2.n_steps) as diffStep

with u, r1, r2, commonIngredients, diffMin, diffStep, 
     (commonIngredients * 2.0 / (diffMin + diffStep + 1)) as score

where not exists((u)-[:REVIEWED]->(r2))
order by score desc
return r2.recipe_name as recommandation, r2.description, score
limit 5
```

### 3. Approche de la requête de recommandation et le code
#### 1. Approche filtrage collaboratif
1. On cherche une recette `r` que utilisateur `p1` avec user_id: `1072593` a évalué et qu'un autre utilisateur `p2` a aussi évalué. On cherche donc les utilisateurs qui ont aussi évalué les recettes que `p1` a évaluées.`x` contient la propriété: rating que `p1` a donné à cette recette, et `y` contient le rating que `p2` a donné à cette même recette.
```
match (p1:User {user_id: 1072593})-[x:REVIEWED]->(r:Recipe)<-[y:REVIEWED]-(p2:User)
```
2. Pour une recette `r` que `p1` et `p2` ont évalué, on calcule le dot product des vecteurs `x` et `y`, et les valeurs `xLength` et `yLength` pour les vecteurs de rating `x` et `y` respectivement afin de pouvoir calculer la métrique de similarité Cosinus.
```
with p1, p2, r,
    sum(x.rating * y.rating) as xyDotProduct,
    sqrt(reduce(xDot = 0.0, a in collect(x.rating) | xDot + a^2)) as xLength,
    sqrt(reduce(yDot = 0.0, b in collect(y.rating) | yDot + b^2)) as yLength
```
3. Puisqu'il est possible d'avoir des ratings de 0 pour les recettes que `p1` et `p2` ont évalué, il faut éliminer ces cas pour ne faire de division par 0 dans la prochaine étape.
```
where xLength > 0 and yLength > 0
```
4. On calcule `sim`, la métrique de similarité Cosinus et on peut classer les `p2` selon leur similarité avec `p1`.
```
with p1, p2, xyDotProduct / (xLength * yLength) as sim
order by sim desc
```
5. On cherche les recettes à recommander `rec` que `p2` ont évalué, mais qui n'ont pas été évaluées par `p1`. On retourne les top 5 recettes recommandées avec leur description et leur score Cosinus.
```
match (p2)-[:REVIEWED]->(rec:Recipe)
where not (p1)-[:REVIEWED]->(rec)
return rec.recipe_name as recommandation,rec.description as description, sim as cosinusScore
limit 5
```
Ex.

recommandation: "szechuan noodles with spicy beef sauce" 

description: "tired of using ground beef the same old way? try this spicy dish! feel free to double the sauce if you like it really saucy! update: the hoisin sauce is quite sweet, so you might start off with just a little and work your way up!"  

cosinusScore: 1.0


#### 2. Approche basée contenu

1. Pour l'utilisateur avec le user_id: `1072593`, on cherche toutes les recettes qu'il a évalué: `reviewedRecipes`.
```
match (u:User {user_id: 1072593})-[:REVIEWED]->(r:Recipe)
with u, collect(r) AS reviewedRecipes
```
2. Avec la première ligne, on cherche des pairs de recettes `r1` et `r2` qui ont un ingrédient en commun. La 2e ligne s'assure que `r1` fait partie des recettes que l'utilisateur `1072593` a évalué (`reviewedRecipes`) et assure que cette recette n'est pas pareil à `r2`.
```
match (r1:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)<-[:HAS_INGREDIENT]-(r2:Recipe)
where r1 in reviewedRecipes and r1 <> r2
```
3. Pour les pairs de recettes, on compte le nombre d'ingrédients en commun, la différence entre le nombre de temps de préparation `diffMin` et entre le nombre d'étapes `diffSteps`. 

```
with u, r1, r2,
    count(i) as commonIngredients,
    abs(r1.minutes - r2.minutes) as diffMin,
    abs(r1.n_steps - r2.n_steps) as diffStep
```
4. Un nombre de `commonIngredients` élevé et des valeurs basses de `diffMin` et `diffSteps` indiquerait que ces deux recettes sont plutôt similaires. Selon cette logique, on peut définir qu'un ratio de `commonIngredients` sur `diffMin` et `diffStep` élevé indique deux recettes plus similaires. On crée un score de similitude basé sur ce ratio. On donne plus d'importance au facteur de `commonIngredients` en le multipliant par 2. Il faut s'assurer que le dénominateur n'égale pas à 0 à aucune instance, donc on additionne 1 à la somme de `diffMin` et `diffStep`.
```
with u, r1, r2, commonIngredients, diffMin, diffStep, 
     (commonIngredients * 2.0 / (diffMin + diffStep + 1)) as score
```
5. On s'assure la recette que l'on recommande `r2` n'a pas été évaluée par l'utilisateur. On retourne les top 5 recettes avec les scores les plus élevés.
```
where not exists((u)-[:REVIEWED]->(r2))
order by score desc
return r2.recipe_name as recommandation, score
limit 5
```
On obtient une table avec le nom des 5 recettes recommandées pour utilisateur `1072593`, leur description et le score.

Ex.

recommandation: "honey pumpkin bundt cake" 

description: "try this one for your thanksgiving buffet!"   

score: 12.0
