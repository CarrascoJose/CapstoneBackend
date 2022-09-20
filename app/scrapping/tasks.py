#Scraping
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup as bs
import lxml

#import json
import os
import re
import functools

from celery import shared_task

from .models import Basket
from .serializers import TestSerializer

def acuenta_scraper(basket):
    cheap_basket = []
    total_price = 0

    session = HTMLSession()
    headers = {
            'User-Agent': 'My User Agent 1.0', 
        }

    for product in basket:

        # Using requests_html library to be able to wait the page to be loaded and then scrape the website
        r = session.get(f'https://www.acuenta.cl/search?name={product}',headers=headers)
        r.html.render(sleep=5,timeout=20)
        html = r.html.html

        # Scraping
        soup = bs(html,'lxml')

        prices_texts = soup.find_all('p',class_='prod--default__price__current')
        
        min_price_tag = functools.reduce(lambda p,c: p if int(re.sub('[\$,.]','',p.text)) < int(re.sub('[\$,.]','',c.text) ) else c,prices_texts)
        
        # Getting data
        price = min_price_tag.text
        product_name = min_price_tag.parent.parent.find('p',class_='prod__name').span.text
        
        # Saving data
        prod = {}
        prod['name'] = product_name
        prod['price'] = price

        cheap_basket.append(product)
        total_price += int(re.sub('[\$,.]','',price))
    
    cheap_data = {
        'cheap_basket': cheap_basket,
        'total_price' : total_price
    }
    
    return cheap_data


def lider_scrapper(basket):
    cheap_basket = []
    total_price = 0
    for product in basket:
        # Scraping
        r = requests.get(f'https://www.lider.cl/supermercado/search?Ns=sku.internetPrice%7C0&Ntt={product}').text
        soup = bs(r, 'lxml')

        most_cheap = soup.find('div',class_='product-details')
        
        # Getting data
        product_name = most_cheap.find('span',class_='product-description').text
        price = most_cheap.find('span',class_='price-sell').text

        # Saving data
        prod = {}
        prod['name'] = product_name
        prod['price'] = price

        cheap_basket.append(product)
        total_price += int(re.sub('[\$,.]','',price))
    
    cheap_data = {
        'cheap_basket': cheap_basket,
        'total_price' : total_price
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
        basket_data = basket_serializer.data['basket']['products']
        lider = lider_scrapper(basket_data)
        acuenta = acuenta_scraper(basket_data)

        # NOTE AQUI IRÍA LA COMPARACIÓN DE LOS PRECIOS
        lider_price = lider['total_price']
        acuenta_price = acuenta['total_price']

        # NOTE ARREGLAR
        if(lider_price<acuenta_price):
            basket.first_market = "lider"
        else:
            basket.first_market = "acuenta"

        basket.save()
        return basket.first_market

    except Exception as e:
        basket.first_masket = "error"
        print(e)
    
    
