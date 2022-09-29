import asyncio

from celery import shared_task

from .models import Basket
from .serializers import TestSerializer
from .scraping_func import market_scraper, get_lider_urls, get_acuenta_urls


@shared_task
def compare(basket_id):
    basket = Basket.objects.get(id=basket_id)
    try:
        basket_serializer = TestSerializer(basket)
        
        # Get the list with the most cheap products and the total price of the basket
        basket_data = basket_serializer.data['basket']['products']
        
        lider_urls = get_lider_urls(basket_data)
        acuenta_urls = get_acuenta_urls(basket_data)

        # Mapping urls
        urls = {
            'lider':lider_urls,
            'acuenta':acuenta_urls
        }

        # Start the event loop to run asynchronous web scraper
        results = asyncio.get_event_loop().run_until_complete(market_scraper(urls))
        print(results)
        #TODO: MEJORAR LAS EXCEPCIONES Y VER CASOS DE RETURN
        basket.save()
        return basket.first_market

    except Exception as e:
        basket.first_masket = "error"
        print(e)
    
    
