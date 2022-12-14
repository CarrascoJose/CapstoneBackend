import asyncio

from celery import shared_task
from celery_progress.backend import ProgressRecorder
from celery.exceptions import SoftTimeLimitExceeded

from .models import Basket
from .serializers import PostBasketSerializer

from .scraping_func import market_scraper
from .get_urls import get_lider_urls, get_acuenta_urls, get_jumbo_urls, get_sisabel_urls
import time



@shared_task(bind=True, time_limit=500)
def compare(self,id):
    instance = Basket.objects.get(pk=id)

    try:
        result = 2
        t1 = time.perf_counter()
        # Get the list with the most cheap products and the total price of the basket
        basket_data = instance.basket
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
        #result = asyncio.get_event_loop().run_until_complete(market_scraper(urls,progress_recorder))
        result = asyncio.run(market_scraper(urls,progress_recorder))

        t2 = time.perf_counter()
        
        instance.ranking = result
        instance.search_duration = round(t2-t1,3)
        instance.save()
        return result

    except SoftTimeLimitExceeded:
        return []
    
    
