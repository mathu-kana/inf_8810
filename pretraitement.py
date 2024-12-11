import pandas as pd
import random
import re

def preprocess_reviews(recipes_file, reviews_file, output_reviews_file):
    # chargement des fichiers .csv d'entrée en dataframe
    recipes_data = pd.read_csv(recipes_file)
    reviews_data = pd.read_csv(reviews_file)

    # récupérer les id recette
    recipe_ids = set(recipes_data['id'])

    # filtrer raw_reviews.csv afin de garder les reviews des recettes dans recipes.csv
    filtered_reviews = reviews_data[reviews_data['recipe_id'].isin(recipe_ids)]
    filtered_reviews.to_csv(output_reviews_file, index=False) # sauvegarde

    print(f"Nombre de rangées dans '{output_reviews_file}': {len(filtered_reviews)}.")
    print(f"Sauvegarde de: \n{output_reviews_file}.")
    return

def preprocess_recipes(recipes_file, output_recipes_file, reviews_file, output_reviews_file, sample_size=100):
    data = pd.read_csv(recipes_file) # charger le fichier .csv en Dataframe
    
    # nettoyer la colonne des ingrédients
    if 'ingredients' in data.columns:
        data['ingredients'] = (
            data['ingredients']
            .str.strip("[]")  # enlève les crochets
            .str.replace(r"[\"']", "", regex=True)  # enlève les guillemets anglais simples et doubles
            .str.replace(", ", "|")  # remplace virgules avec |
        )

    # échantillonnage
    if len(data) <= sample_size:
        data.to_csv(output_recipes_file, index=False) # pas d'échantillonnage
    else:
        sampled_data = data.sample(n=sample_size, random_state=99) # échantillonner 100 recettes/rangées

        # sauvegarder 'sampled_recipes.csv'
        sampled_data.to_csv(output_recipes_file, index=False)
        print(f"Échantillon de {sample_size} recettes et sauvegarde de:\n{output_recipes_file}")
    

    preprocess_reviews(recipes_file, reviews_file, output_reviews_file)

    return

#inputs
#TODO changer les paths
# Chemins des fichiers doivent être ceux aux fichiers dans le repertoire d'importation de Neo4j
# recipes_file = 'raw_recipes.csv'  
# output_recipes_file = 'recipes.csv'
# reviews_file = 'raw_reviews.csv'
# output_reviews_file = 'reviews.csv'

recipes_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/raw_recipes.csv'  
output_recipes_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/recipes.csv'
reviews_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/raw_reviews.csv'
output_reviews_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/reviews.csv'

preprocess_recipes(recipes_file, output_recipes_file, reviews_file, output_reviews_file, sample_size=100)