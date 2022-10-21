import asyncio

from celery import shared_task
from celery_progress.backend import ProgressRecorder

from .models import Basket
from .serializers import PostBasketSerializer

from .scraping_func import market_scraper
from .get_urls import get_lider_urls, get_acuenta_urls, get_jumbo_urls, get_sisabel_urls
import time

@shared_task(bind=True)
def compare(self,id):
    basket = Basket.objects.get(id=id)
    try:
        basket_serializer = PostBasketSerializer(basket)
        # Get the list with the most cheap products and the total price of the basket
        basket_data = basket_serializer.data['basket']
        lider_urls = get_lider_urls(basket_data)
        acuenta_urls = get_acuenta_urls(basket_data)
        jumbo_urls = get_jumbo_urls(basket_data)
        sisabel_urls = get_sisabel_urls(basket_data)

        # Mapping urls  
        urls = {
            'lider':lider_urls,
            'acuenta':acuenta_urls,
            'jumbo':jumbo_urls,
            'santa_isabel':sisabel_urls
        }

        progress_recorder = ProgressRecorder(self)

        # Start the event loop to run asynchronous web scraper
        result = asyncio.get_event_loop().run_until_complete(market_scraper(urls,progress_recorder))

        
        basket.ranking = result
        basket.save()
        return result

    except Exception as e:
        print(e)
    
    
