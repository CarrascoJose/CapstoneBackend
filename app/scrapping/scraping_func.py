import asyncio
from bs4 import BeautifulSoup
import requests_html
from requests_html import AsyncHTMLSession

import time
import functools
import re
from .utils import format_to_int, total_sum

# Get urls from each market given the basket passed by the user
def get_lider_urls(basket):
    return [f'https://www.lider.cl/supermercado/search?Ns=sku.internetPrice%7C0&Ntt={product}' for product in basket]

def get_acuenta_urls(basket):
    return [f'https://www.acuenta.cl/search?name={product}' for product in basket]
######################

async def fetch_html(url:str, session:AsyncHTMLSession, sleep: int):
    # Async coroutine to fetch and render the pages
    r = await session.get(url)
    print(f"Response received of: {url}")
    if sleep>0:
        await r.html.arender(sleep=sleep,timeout=20)
    print(f"Rendered: {url}")
    return r

async def get_soup(url: str, session: AsyncHTMLSession, sleep: int):
    # Block of code to get the html and parse
    try:
        r = await fetch_html(url=url, session=session, sleep=sleep)
    except Exception as e:
        raise Exception("Error al realizar la petición")
    else:
        html = r.html.html
        soup = BeautifulSoup(html,'lxml')
        return soup 


async def lider_scraper(url: str, session: AsyncHTMLSession, sleep: int):
    # Async coroutine to implement the lider web scraper
    try:
        soup = await get_soup(url=url, session=session, sleep=sleep)
        product_name = soup.find('span',class_='product-description').string
        price = soup.find('span',class_='price-sell').string

        tries = 0

        while ((product_name is None) or (price is None)) and tries<2:
            print("Reintentando...")
            soup = await get_soup(url=url, session=session, sleep=sleep)
            product_name = soup.find('span',class_='product-description').string
            price = soup.find('span',class_='price-sell').string
            tries+=1

        if tries>1:
            raise RuntimeError("Número de intentos de carga superados")

        return {
            'name':product_name,
            'price':format_to_int(price)
        }

    except Exception as e:
        print(e)
        return {
            'name':"Producto no encontrado",
            'price':0
        }

async def acuenta_scraper2(url: str, session: AsyncHTMLSession, sleep: int):
    # Async coroutine to implement the lider web scraper
    try:
        soup = await get_soup(url=url, session=session, sleep=sleep)
        prices = soup.find_all('p',class_='prod--default__price__current')

        tries = 0
        while len(prices)<1 and tries<2:
            print("Reintentando...")
            soup = await get_soup(url=url, session=session, sleep=sleep)
            prices = soup.find_all('p',class_='prod--default__price__current')
            tries+=1
        
        if tries>1:
            raise RuntimeError("Número de intentos de carga superados")

        min_price_tag = functools.reduce(lambda a,b: a if int(re.sub('[\$,.]','',a.string)) < int(re.sub('[\$,.]','',b.text)) else b, prices)

        min_price = min_price_tag.string

        product_name = min_price_tag.parent.parent.find('p',class_='prod__name').span.string

        return {
            'name':product_name,
            'price':format_to_int(min_price)
        }    

    except Exception as e:
        print(e)
        return {
            'name':"Producto no encontrado",
            'price':0
        }

async def market_scraper(urls):
    # Initializating session and tasks for each market and their respective urls
    session = AsyncHTMLSession()
    lider_tasks = asyncio.gather(*[lider_scraper(url,session,0) for url in urls['lider']])
    acuenta_tasks = asyncio.gather(*[acuenta_scraper2(url,session,3) for url in urls['acuenta']])
    
    # Gathering the tasks and await them
    results = await asyncio.gather(lider_tasks,acuenta_tasks)

    sum_lider, sum_acuenta = total_sum(results[0]), total_sum(results[1])

    print(f"Lider total: {sum_lider}\n\n")
    print(f"Acuenta total: {sum_acuenta}\n\n")

    final_data = {
        'lider':sum_lider,
        'acuenta':sum_acuenta
    }

    # Close session and return
    await session.close()
    return f"Most cheap in: {min(final_data, key=final_data.get)}"