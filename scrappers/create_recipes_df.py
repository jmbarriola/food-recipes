from food_scrapper import make_request, make_soup, mise_en_place
import re
import time
import json
import random
import logging
import argparse

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
NUM_REGEX = re.compile(r'\d+') 
# Final df

RECIPE_FILE_NAME = 'recipes.json'
RECIPE_KEYS = ['recipe_number','recipe_name','recipe_name_check', 'ingredients_list', 'categories_list',
                    'cal','fat','carb','prot','chol','sod','prep_time', 'rating', 'reviews', 'photos']

def parse_args():
    '''Parse the program arguments'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', default=False, help='activate debug output')
    parser.add_argument('--recipes-db', default=RECIPE_FILE_NAME, help='DB file to keep recipes')
    # If you remove the "default", then these become _mandatory_ arguments, which could be useful
    parser.add_argument('--loop-lower', type=int, default=10020)
    parser.add_argument('--loop-upper', type=int, default=10050)
    return parser.parse_args()

def update_db(db_filepath, more_recipes):
    '''Add more recipes to the DB file (is created if it doesn't exist)'''
    try:
        with open(db_filepath, 'r') as db_file:
            recipes = json.load(db_file)
    except OSError:
        recipes = []
    recipes.extend(more_recipes)
    with open(db_filepath, 'w') as db_file:
        json.dump(recipes, db_file)

def fetch_and_soupify_recipe(index):
    '''Download, soupify, parse and return a single recipe or None.

    On error don't crash: print a warning and a stacktrace.
    '''
    url='https://allrecipes.com/recipe/{}'.format(index)
    try:
        request = make_request(url, HEADERS)
    except Exception as e:
        logging.warning('could not download {}'.format(url))
        logging.exception(e)
        return None  # log the error and move on
    soup = make_soup(request)
    if [ing.text for ing in soup.find_all(itemprop="recipeIngredient")]:
        recipe_values = mise_en_place(soup=soup,regex=NUM_REGEX)
        recipe_values.insert(0, index)
        return dict(zip(RECIPE_KEYS, recipe_values))
    return None

if __name__ == '__main__':
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    new_recipes = []
    for ix in range(args.loop_lower, args.loop_upper):
        time.sleep(1 + random.random())
        print(ix)
        recipe = fetch_and_soupify_recipe(ix)
        if recipe is not None:
            new_recipes.append(recipe)

    # Finally, update the recipes database
    update_db(RECIPE_FILE_NAME, new_recipes)