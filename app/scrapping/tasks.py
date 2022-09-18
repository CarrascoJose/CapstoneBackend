#Scraping
from math import prod
import requests
from bs4 import BeautifulSoup as bs
import json
import lxml
from celery import shared_task

from .models import Basket
from .serializers import TestSerializer

def lider_scrapper(basket):
    each_most_cheaps = []
    for product in basket:
        url = ''
        if(product=='Jamón-de-Pavo-y-Pollo'):
            url = 'https://www.lider.cl/supermercado/category/Frescos-y-L%C3%A1cteos/Fiambres-y-Embutidos/Jam%C3%B3n-de-Pavo-y-Pollo/_/N-b3xyq7?Ns=sku.internetPrice%7C0'
        elif(product=='Carnes-para-Parrilla'):
            url = 'https://www.lider.cl/supermercado/category/Carnes-y-Pescados/Vacuno/Carnes-para-Parrilla/_/N-y03maf?Ns=sku.internetPrice%7C0#'
        r = requests.get(url).text
        soup = bs(r, 'lxml')

        most_cheap = soup.find('div',class_='product-details')
        
        product = {}
        product_name = most_cheap.find('span',class_='product-description').text
        product['name'] = product_name
        each_most_cheaps.append(product)
        #price = most_cheap.find('span',class_='price-sell').text
    return each_most_cheaps


@shared_task
def compare(basket_id):
    basket = Basket.objects.get(id=basket_id)
    try:
        basket_serializer = TestSerializer(basket)
        lider = lider_scrapper(basket_serializer.data['basket']['products'])
        print(lider)
        basket.first_market = "lider"
        basket.save()
        return lider
    except Exception as e:
        basket.first_masket = "error"
        print(e)
    
    
