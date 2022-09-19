#Scraping

import requests
from bs4 import BeautifulSoup as bs
import lxml

import json
import os
import re

from celery import shared_task

from .models import Basket
from .serializers import TestSerializer

def lider_scrapper(basket, categories):
    cheap_basket = []
    total_price = 0
    for product in basket:
        r = requests.get(categories[product]).text
        soup = bs(r, 'lxml')

        most_cheap = soup.find('div',class_='product-details')
        
        product_name = most_cheap.find('span',class_='product-description').text
        price = most_cheap.find('span',class_='price-sell').text

        product = {}
        product['name'] = product_name
        product['price'] = price

        cheap_basket.append(product)

        total_price += int(re.sub('[\$,.]','',price))
    
    cheap_data = {
        'cheap_basket': cheap_basket,
        'price' : total_price
    }
    
    return cheap_data


@shared_task
def compare(basket_id):
    basket = Basket.objects.get(id=basket_id)
    try:
        basket_serializer = TestSerializer(basket)
        
        #Getting the specific categories of the products, the user will select a list of them for build his basket.
        # NOTE ESTO HAY QUE VERLO PORQUE ES DISTINTO PARA VARIOS SUPERMERCADOS, ENTONCES HAY QUE ARMAR DE ALGUNA FORMA UNA LISTA UNIVERSAL DE PRODUCTOS. ESTA POR EL MOMENTO LA HICE CON LAS CATEGORIAS DEL LIDER, QUE LAS SAQUE CON UN SCRAPER DE LAS CATEGORIAS Y LAS METI EN EL TXT PARA PROBARLO
        with open(os.path.join(os.path.dirname(__file__), 'categories.txt')) as f:
            categories_data = json.load(f)

        # Web Scrapping multiple markets
        # This has to be asynchronous and we must execute all of them simultaneously and wait for the result of all of them
        # Investigar async
        
        # Get the list with the most cheap products and the total price of the basket
        lider = lider_scrapper(basket_serializer.data['basket']['products'], categories_data)

        # NOTE AQUI IRÍA LA COMPARACIÓN DE LOS PRECIOS
        basket.first_market = "lider"
        basket.save()
        return lider

    except Exception as e:
        basket.first_masket = "error"
        print(e)
    
    
