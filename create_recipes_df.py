from food_scrapper import *
import pandas as pd
import re
import json
import os

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
num_regex = re.compile('\d+')


# Final df

recipe_file_name = 'recipes_test.json'
recipe_keys = ['recipe_number','recipe_name','recipe_name_check', 'ingredients_list', 'categories_list',
                    'cal','fat','carb','prot','chol','sod','prep_time', 'rating', 'reviews', 'photos']

for i in range(10000,10020):
    url='https://allrecipes.com/recipe/{}'.format(i)
    request = make_request(url, headers)
    soup = make_soup(request)
    if [ing.text for ing in soup.find_all(itemprop="recipeIngredient")]:
        recipe_values = mise_en_place(soup=soup,regex=num_regex)
        recipe_values.insert(0,i)
        recipe_dict = dict(zip(recipe_keys, recipe_values))
        print(recipe_dict)
        if not os.path.isfile(recipe_file_name):
            with open(recipe_file_name, 'w') as json_file:
                 json.dump(recipe_dict, json_file)
        else:
            with open(recipe_file_name, 'r+') as json_file:
                dic = json.load(json_file)
                print(dic)
                dic.update(recipe_dict)
                print(dic)
                json.dump(dic, json_file)
        print('Writing recipe number {}'.format(i))
        
    time.sleep(1.1)