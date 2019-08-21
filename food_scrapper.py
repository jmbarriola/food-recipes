import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re

def make_request(url,headers):
    response = requests.get(url=url, headers=headers)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        print("Error: " + str(e))
    return response

def make_soup(response):
    soup = BeautifulSoup(response.content,"html.parser")
    return soup

def fetch_title(soup):
    # Recipe title
    recipe_name = soup.title.text
    return recipe_name

def fetch_ingredients(soup):
     # Ingredients list
    ingredients_list = [ing.text for ing in soup.find_all(itemprop="recipeIngredient")]
    # Filter empty elements
    ingredients_list = list(filter(None, ingredients_list))
    return ingredients_list

def fetch_categories(soup):
    # Categories list. Strips withspace
    categories_list = [ing.text.strip() for ing in soup.find_all(itemprop="name")]
    # Filter empty elements
    categories_list = list(filter(None, categories_list))
    return categories_list

def fetch_calories(soup,regex):
    # Extracts the numbers of calories
    return regex.search(soup.find(itemprop="calories").text.strip()).group()

def fetch_nutrients(soup, nutrient_name):
    # Extract name and strips whitespace
    return soup.find(itemprop=nutrient_name).text.strip()

def fetch_prep_time(soup):
    # Prep Time
    prep_time = soup.find('span',class_="ready-in-time")
    # Extract time if possible
    prep_time = prep_time.text if prep_time is not None else prep_time
    return prep_time

def fetch_social_data(soup, item):
    return soup.find('meta',itemprop=item)['content']

def fetch_photo_count(soup, regex):
    return regex.search(soup.find('span',class_="picture-count-link").text).group()

def mise_en_place(soup, regex):
    
    # Ingredients list
    ingredients_list = fetch_ingredients(soup)
    
    # Categories list
    categories_list = fetch_categories(soup)
    
    # Recipe name
    recipe_name = categories_list[-1]

    # Recipe name check
    recipe_name_check = fetch_title(soup)
    
    # Nutritional info
    # Calories
    cal=fetch_calories(soup,regex)
    # Fat
    fat=fetch_nutrients(soup, nutrient_name="fatContent")
    # Carbs
    carb=fetch_nutrients(soup, nutrient_name="carbohydrateContent")
    # Protein
    prot=fetch_nutrients(soup, nutrient_name="proteinContent")
    # Cholesterol
    chol=fetch_nutrients(soup, nutrient_name="cholesterolContent")
    # Sodium
    sod=fetch_nutrients(soup, nutrient_name="cholesterolContent")    
    
    # Prep Time
    prep_time = soup.find('span',class_="ready-in-time")
    prep_time = prep_time.text if prep_time is not None else prep_time 
    
    # Rating
    rating = fetch_social_data(soup, item="ratingValue")

    # Reviews
    reviews = fetch_social_data(soup, item="reviewCount")
    
    # Photos
    photos = fetch_photo_count(soup, regex)

    return [recipe_name,recipe_name_check, ingredients_list, categories_list,cal,fat,carb,prot,chol,sod,prep_time, rating, reviews, photos]


