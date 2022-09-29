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

async def fetch_html(url:str, session:AsyncHTMLSession):
    # Async coroutine to fetch and render the pages
    r = await session.get(url)
    print(f"Response received of: {url}")
    await r.html.arender(sleep=5,timeout=20)
    #TODO: IMPLEMENTAR CASO PARA CUANDO NO SE ALCANZA A RENDERIZAR O EXISTE UN TIMEOUT
    #NOTE: DE REPENTE TIRA EL SIGUIENTE ERROR O ADVERTENCIA: 
    #NOTE: "Future exception was never retrieved"
    #NOTE: Ver esto en más detalle y mejorarlo
    print(f"Rendered: {url}")
    return r.html.raw_html

#TODO: IMPLEMENTAR MEJOR LAS EXCEPCIONES Y VER LOS CASOS EN QUE NO SE ENCUENTRA ALGUNA ETIQUETA
# OPCIONES: SEGUIR RENDERIZANDO HASTA QUE CARGUE O DEVOLVER OTRO VALOR.
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
            product_name = soup.find('span',class_='product-description').string
            price = soup.find('span',class_='price-sell').string
            return {
                'name':product_name,
                'price':format_to_int(price)
            }
        except Exception as e:
            return {
                'message':f'Element not found. Error: {e}'
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
            min_price_tag = functools.reduce(lambda a,b: a if int(re.sub('[\$,.]','',a.string)) < int(re.sub('[\$,.]','',b.text)) else b, prices)

            min_price = min_price_tag.string

            product_name = min_price_tag.parent.parent.find('p',class_='prod__name').span.string

            return {
                'name':product_name,
                'price':format_to_int(min_price)
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