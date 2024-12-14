'''
INF8810 - Projet 2
Auteurs: 
    - Mathura Kanapathippillai, KANM18619701
    - Imed Eddine Lakehal, LAKI63260006  
    - Andres Felipe Ordonez Bustos, ORDA11119408
8 décembre 2024

Description:
- L'exécution de ce script Python permettra de télécharger le dossier compressé de
l'ensemble de données sur Kaggle: Food.com Recipes and Interactions dans ce repertoire.

- Le dossier sera décompressé.

- Puisque RAW_recipes.csv contient plus de 200k rangées, vous devez entrer en ligne 
de commande la taille de l'échantillon (nombre de recettes à garder) selon vos
ressources computationnelles. La valeur 5000 est recommandée.

    Entrez la taille de l'échantillon ou laissez vide: 

- Le prétraitement des données sera fait et les fichiers recipes.csv et
interactions.csv seront sauvegardés dans ce repertoire. Veuillez les déplacer vers
le repertoire d'importation de Neo4j.

'''


import os
import zipfile
import requests
import pandas as pd

def download_file(url, local_filename):
    # Stream the response to handle large files
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def unzip_data(zip_file_path, extract_dir):
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    print("Files extracted:")
    for f in os.listdir(extract_dir):
        print(f)
    return os.listdir(extract_dir)

def preprocess_reviews(recipes_file, reviews_file, output_reviews_file):
    # chargement des fichiers .csv d'entrée en dataframe
    recipes_data = pd.read_csv(recipes_file)
    reviews_data = pd.read_csv(reviews_file)

    # supprimer les colonnes non-utilisées
    col_a_supprimer = ['date', 'review']
    filtered_reviews = reviews_data.drop(columns=col_a_supprimer, errors='ignore')

    # récupérer les id recette
    recipe_ids = set(recipes_data['id'])

    # filtrer les reviews pertinents aux recettes
    filtered_reviews = filtered_reviews[filtered_reviews['recipe_id'].isin(recipe_ids)]
    filtered_reviews.to_csv(output_reviews_file, index=False) # sauvegarde

    print(f"\nNombre de rangées dans 'interactions.csv': {len(filtered_reviews)}.")
    print(f"Sauvegarde de: {output_reviews_file}")
    return

def preprocess(input_recipes_file, output_recipes_file, input_reviews_file, output_reviews_file, sample_size=None):
    data = pd.read_csv(input_recipes_file) # charger les recettes en Dataframe
    
    # supprimer les colonnes non-utilisées
    col_a_supprimer = ['contributor_id','nutrition']
    data = data.drop(columns=col_a_supprimer, errors='ignore')

    # nettoyer les colonnes des ingrédients et des tags
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

# ===============================================================================================================================================

# URL au dossier compressé contenant RAW_recipes.csv et RAW_interactions.csv
data_url = "https://www.kaggle.com/api/v1/datasets/download/shuyangli94/food-com-recipes-and-user-interactions"
zip_file_name = "data.zip"
extract_dir = "extracted_data"
script_dir = os.path.dirname(os.path.abspath(__file__))

print("Téléchargement du dataset...")
download_file(data_url, zip_file_name)

print("Décompression (unzipping) du dataset...")
files_in_dir = unzip_data(zip_file_name, extract_dir)

# vérification des fichiers d'intérêt
if "RAW_recipes.csv" in files_in_dir and "RAW_interactions.csv" in files_in_dir:
    input_recipes_file = os.path.join(extract_dir, "RAW_recipes.csv")
    output_recipes_file = os.path.join(script_dir, "recipes.csv")
    input_reviews_file = os.path.join(extract_dir, "RAW_interactions.csv")
    output_reviews_file = os.path.join(script_dir, "interactions.csv")

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


    print("\nPrétraitement des fichiers...")
    preprocess(input_recipes_file, output_recipes_file, input_reviews_file, output_reviews_file, sample_size=sample_size)
else:
    print("RAW_recipes.csv ou RAW_interactions.csv non retrouvé.")

print("\n\nFin d'éxecution.\nVeuillez suivre les étapes dans le fichier Markdown et le projet Neo4j.")