import os
import pandas as pd
import random
import re

def preprocess_reviews(recipes_file, reviews_file, output_reviews_file):
    # chargement des fichiers .csv d'entrée en dataframe
    recipes_data = pd.read_csv(recipes_file)
    reviews_data = pd.read_csv(reviews_file)

    # supprimer les colonnes non-utilisées
    col_a_supprimer = ['date', 'review']
    filtered_reviews = reviews_data.drop(columns=col_a_supprimer, errors='ignore')

    # récupérer les id recette
    recipe_ids = set(recipes_data['id'])

    # filtrer RAW_interactions.csv afin de garder les reviews pertinents aux recettes dans recipes.csv
    filtered_reviews = filtered_reviews[filtered_reviews['recipe_id'].isin(recipe_ids)]
    filtered_reviews.to_csv(output_reviews_file, index=False) # sauvegarde

    print(f"\nNombre de rangées dans 'interactions.csv': {len(filtered_reviews)}.")
    print(f"Sauvegarde de: {output_reviews_file}.")
    return

def preprocess(repertoire_path, sample_size=None):
    # chemins aux fichiers
    input_recipes_file = os.path.join(repertoire_path, 'RAW_recipes.csv')
    output_recipes_file = os.path.join(repertoire_path, 'recipes.csv')
    input_reviews_file = os.path.join(repertoire_path, 'RAW_interactions.csv')
    output_reviews_file = os.path.join(repertoire_path, 'interactions.csv')

    data = pd.read_csv(input_recipes_file) # charger les recettes en Dataframe

    # supprimer les colonnes non-utilisées
    col_a_supprimer = ['contributor_id','nutrition']
    data = data.drop(columns=col_a_supprimer, errors='ignore')

    #TODO turn to function
    col_a_nettoyer = ['ingredients','tags']

    for col in col_a_nettoyer:
        if col in data.columns:
            data[col] = (data[col]
                .str.strip("[]")  # enlève les crochets
                .str.replace(r'["\']', "", regex=True)  # enlève les guillemets anglais simples et doubles
                .str.replace(", ", "|")  # remplace virgules avec |
            )

    # échantillonnage si nécessaire
    if sample_size is None:
        data.to_csv(output_recipes_file, index=False)
        print(f"\nPas d'échantillonage. Sauvegarde de {output_recipes_file}")
    else:
        if len(data) <= sample_size:
            data.to_csv(output_recipes_file, index=False)
            print(f"\nPas d'échantillonage. sample_size supérieur au nombre de rangées dans RAW_recipes.csv. Sauvegarde de {output_recipes_file}")
        else:
            sampled_data = data.sample(n=sample_size, random_state=99)
            sampled_data.to_csv(output_recipes_file, index=False)
            print(f"\nÉchantillon de {sample_size} rangées sauvegardé dans:\n{output_recipes_file}")
    
    # pretraitement de RAW_interactions.csv pour garder les reviews pertinents à recipes.csv
    preprocess_reviews(output_recipes_file, input_reviews_file, output_reviews_file)

    return

#inputs
# Les fichiers input doivent être dans le repertoire d'importation de Neo4j
#   - 'RAW_recipes.csv'
#   - 'RAW_interactions.csv

while True:
    repertoire_path = input("Entrez le chemin du répertoire contenant les fichiers CSV (repertoire d'importation Neo4j):\n ").strip()
    if os.path.isdir(repertoire_path):
        break
    else:
        print("Chemin invalide. Veuillez réessayer.")

while True:
    try:
        sample_size_input = input("Entrez la taille de l'échantillon ou laissez vide: ").strip()
        if sample_size_input == "":
            sample_size = None
            break
        sample_size = int(sample_size_input)
        if sample_size > 0:
            break
        else:
            print("Entrée invalide: entier positif requis. Veuillez réessayer.")
    except ValueError:
        print("Entrée invalide. Veuillez entrer un entier positif ou laisser vide.")


# # chemin du repertoire d'importation de Neo4j
# repertoire_path = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import'
# sample_size = 100
# # preprocess(repertoire_path)

preprocess(repertoire_path, sample_size)