import os
import pandas as pd
import random
import re

def preprocess_reviews(recipes_file, reviews_file, output_reviews_file):
    # chargement des fichiers .csv d'entrée en dataframe
    recipes_data = pd.read_csv(recipes_file)
    reviews_data = pd.read_csv(reviews_file)

    # récupérer les id recette
    recipe_ids = set(recipes_data['id'])

    # filtrer RAW_interactions.csv afin de garder les reviews pertinents aux recettes dans recipes.csv
    filtered_reviews = reviews_data[reviews_data['recipe_id'].isin(recipe_ids)]
    filtered_reviews.to_csv(output_reviews_file, index=False) # sauvegarde

    print(f"Nombre de rangées dans 'interactions.csv': {len(filtered_reviews)}.")
    print(f"Sauvegarde de: \n{output_reviews_file}.")
    return

def preprocess_recipes(repertoire_path, sample_size=100):
    # chemins aux fichiers
    input_recipes_file = os.path.join(repertoire_path, 'RAW_recipes.csv')
    output_recipes_file = os.path.join(repertoire_path, 'recipes.csv')
    input_reviews_file = os.path.join(repertoire_path, 'RAW_interactions.csv')
    output_reviews_file = os.path.join(repertoire_path, 'interactions.csv')

    data = pd.read_csv(input_recipes_file) # charger les recettes en Dataframe
    
    # nettoyer la colonne des ingrédients
    if 'ingredients' in data.columns:
        data['ingredients'] = (
            data['ingredients']
            .str.strip("[]")  # enlève les crochets
            .str.replace(r"[\"']", "", regex=True)  # enlève les guillemets anglais simples et doubles
            .str.replace(", ", "|")  # remplace virgules avec |
        )
    #TODO remove, temporaire pour sauver du temps
    # échantillonnage
    if len(data) <= sample_size:
        data.to_csv(output_recipes_file, index=False) # pas d'échantillonnage
    else:
        sampled_data = data.sample(n=sample_size, random_state=99) # échantillonner 100 recettes/rangées

        # sauvegarder 'recipes.csv'
        sampled_data.to_csv(output_recipes_file, index=False)
        print(f"Échantillon de {sample_size} recettes et sauvegarde de:\n{output_recipes_file}")
    
    # pretraitement de RAW_interactions.csv pour garder les reviews pertinents à recipes.csv
    preprocess_reviews(output_recipes_file, input_reviews_file, output_reviews_file)

    return

#inputs
#TODO changer les paths
# Les fichiers input doivent être dans le repertoire d'importation de Neo4j
#   - 'RAW_recipes.csv'
#   - 'RAW_interactions.csv

# chemin du repertoire d'importation de Neo4j
repertoire_path = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import'

preprocess_recipes(repertoire_path, sample_size=100)