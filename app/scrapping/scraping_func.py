import asyncio
from bs4 import BeautifulSoup
import requests_html
from requests_html import AsyncHTMLSession

import time
import functools
import re

# Get urls from each market given the basket passed by the user
def get_lider_urls(basket):
    return [f'https://www.lider.cl/supermercado/search?Ns=sku.internetPrice%7C0&Ntt={product}' for product in basket]

def get_acuenta_urls(basket):
    return [f'https://www.acuenta.cl/search?name={product}' for product in basket]
######################

async def fetch_html(url:str, session:AsyncHTMLSession):
    # Async coroutine to fetch and render the pages
    r = await session.get(url)
    print(f"Response received of: {url}")
    await r.html.arender(sleep=3,timeout=20)
    print(f"Rendered: {url}")
    return r.html.raw_html

async def lider_scraper(url: str, session: AsyncHTMLSession):
    # Async coroutine to implement the lider web scraper
    try:
        html = await fetch_html(url=url, session=session)

    except Exception as e:
        print(f"Error fetching the url: {url} \t Message: {e.message}")
        return {}
    else:
        # Here's the magic
        # WebScraper
        # Maybe change BeautifulSoup
        try:
            soup = BeautifulSoup(html,'lxml')
            product_name = soup.find('span',class_='product-description').text
            price = soup.find('span',class_='price-sell').text
            return {
                'name':product_name,
                'price':price
            }
        except Exception as e:
            return {
                'message':'Element not found'
            }

async def acuenta_scraper(url: str, session: AsyncHTMLSession):
    # Async coroutine to implement the lider web scraper
    try:
        html = await fetch_html(url=url, session=session)

    except Exception as e:
        print(f"Error fetching the url: {url} \t Message: {e.message}")
        return {}
    else:
        # Here the magic
        try:
            soup = BeautifulSoup(html,'lxml')
            prices = soup.find_all('p',class_='prod--default__price__current')
            min_price_tag = functools.reduce(lambda a,b: a if int(re.sub('[\$,.]','',a.text)) < int(re.sub('[\$,.]','',b.text)) else b, prices)

            min_price = min_price_tag.text

            product_name = min_price_tag.parent.parent.find('p',class_='prod__name').span.text

            return {
                'name':product_name,
                'price':min_price
            }
            
        except Exception as e:
            return {
                'message':f'Element not found. Error: {e}'
            }

async def market_scraper(urls):
    # Initializating session and tasks for each market and their respective urls
    session = AsyncHTMLSession()
    lider_tasks = asyncio.gather(*[lider_scraper(url,session) for url in urls['lider']])
    acuenta_tasks = asyncio.gather(*[acuenta_scraper(url,session) for url in urls['acuenta']])
    
    # Gathering the tasks and await them
    results = await asyncio.gather(lider_tasks,acuenta_tasks)

    # Close session and return
    await session.close()
    return results