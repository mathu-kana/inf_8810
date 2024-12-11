import pandas as pd
import random
import re

def preprocess_recipes(input_file, output_file):
    data = pd.read_csv(input_file) # charger le fichier .csv en Dataframe
    
    # nettoyer la colonne des ingrédients
    if 'ingredients' in data.columns:
        data['ingredients'] = (
            data['ingredients']
            .str.strip("[]")  # enlève les crochets
            .str.replace(r"[\"']", "", regex=True)  # enlève les guillemets anglais simples et doubles
            .str.replace(", ", "|")  # remplace virgules avec |
        )

    # échantillonnage
    if len(data) <= 100:
        data.to_csv(output_file, index=False) # pas d'échantillonnage
    else:
        sampled_data = data.sample(n=100, random_state=99) # échantillonner 100 recettes/rangées

        # sauvegarder 'sampled_recipes.csv'
        sampled_data.to_csv(output_file, index=False)
        print(f"Échantillon de 1000 recettes et sauvegarde de:\n{output_file}")
    return

#inputs
#TODO changer les paths
# recipes_file = 'recipes.csv'  
# sampled_recipes_file = 'sampled_recipes.csv'
recipes_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/recipes.csv'  
sampled_recipes_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/sampled_recipes.csv'

preprocess_recipes(recipes_file, sampled_recipes_file)