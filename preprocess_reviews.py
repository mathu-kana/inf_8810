import pandas as pd

#TODO changer le tout en fonction et input ce sont les path vers les fichiers

def preprocess_reviews(recipes_file, reviews_file, filtered_reviews_file):
    # chargement des fichiers .csv d'entrée en dataframe
    recipes_data = pd.read_csv(recipes_file)
    reviews_data = pd.read_csv(reviews_file)

    # récupérer les id recette
    recipe_ids = set(recipes_data['id'])

    # filter reviews.csv afin de garder les reviews des recettes dans sampled_recipes.csv
    filtered_reviews = reviews_data[reviews_data['recipe_id'].isin(recipe_ids)]
    filtered_reviews.to_csv(output_file, index=False) # sauvegarde

    print(f"Nombre de rangées dans 'filtered_reviews.csv': {len(filtered_reviews)}.")
    print(f"Sauvegarde de: \n{output_file}.")
    return

#inputs
recipes_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/sampled_recipes.csv'
reviews_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/reviews.csv'
output_file = '/Users/mathu/Desktop/uqam/Trimestre_4-5/inf8810/import/filtered_reviews.csv'
