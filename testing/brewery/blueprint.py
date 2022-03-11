from flask import Blueprint
from .models import session, Brewery, Beer, Style, Category
import sys
import os

def updir(path, levels=2):
    for i in range(levels):
        path = os.path.dirname(path)
    return path

thisDir = os.path.abspath(os.path.dirname(__file__))
libPath = updir(thisDir)
print(libPath)
sys.path.append(libPath)
from flask_servant import create_api, create_service

brewery_blueprint = Blueprint(
    'breweries_api',
    __name__, 
    # static_folder=staticDir, 
    # url_prefix='/brewery-api'
)

brewery_service = create_service(
    'Breweries', 
    'service for brewery data', 
    '/breweries',
    Brewery,
    session
)

beer_service = create_service(
    'Beers', 
    'service for beers data', 
    '/beers',
    Beer,
    session
)

style_service = create_service(
    'Styles', 
    'service for beer style data', 
    '/beers',
    Style,
    session
)

category_service = create_service(
    'Categories', 
    'service for beer category data', 
    '/beers',
    Category,
    session
)

api = create_api(
    brewery_blueprint,
    'Brewery API',
    'API methods for brewery data',
    # namespaces=[brewery_service, beer_service ],
    doc='/help'
)
print('api?', api)