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

def lider_scrapper(basket):
    cheap_basket = []
    total_price = 0
    for product in basket:
        r = requests.get(f'https://www.lider.cl/supermercado/search?Ns=sku.internetPrice%7C0&Ntt={product}').text
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

        # Web Scrapping multiple markets
        # This has to be asynchronous and we must execute all of them simultaneously and wait for the result of all of them
        # Investigar async
        
        # Get the list with the most cheap products and the total price of the basket
        lider = lider_scrapper(basket_serializer.data['basket']['products'])

        # NOTE AQUI IRÍA LA COMPARACIÓN DE LOS PRECIOS
        basket.first_market = "lider"
        basket.save()
        return lider

    except Exception as e:
        basket.first_masket = "error"
        print(e)
    
    
