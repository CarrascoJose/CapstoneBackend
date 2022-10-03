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

def get_jumbo_urls(basket):
  return ["https://www.jumbo.cl/busqueda?ft="+product.replace(' ', '%20')+"&o=OrderByPriceASC&page=1" for product in basket]

def get_sisabel_urls(basket):
  return ["https://www.santaisabel.cl/busqueda?ft="+product.replace(' ', '%20')+"&o=OrderByPriceASC&page=1" for product in basket]
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
        product_name = soup.find('span',class_='product-description')
        price = soup.find('span',class_='price-sell')

        tries = 0

        while ((product_name is None) or (price is None)) and tries<2:
            print("Reintentando...")
            soup = await get_soup(url=url, session=session, sleep=sleep)
            product_name = soup.find('span',class_='product-description')
            price = soup.find('span',class_='price-sell')
            tries+=1

        if tries>1:
            raise RuntimeError("Número de intentos de carga superados")

        return {
            'name':product_name.string,
            'price':format_to_int(price.string)
        }

    except Exception as e:
        print(e)
        return {
            'name':"Producto no encontrado",
            'price':0
        }

async def acuenta_scraper(url: str, session: AsyncHTMLSession, sleep: int):
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

async def cencosud_scraper(url: str, session: AsyncHTMLSession, sleep: int):
  try:
    soup  = await get_soup(url, session, sleep)
    all_items = soup.find_all('div', class_="shelf-product-island")

    tries = 0
    while len(all_items)<1 and tries<2:
      print("Reintentando...Jumbo...")
      soup  = await get_soup(url, session, sleep)
      all_items = soup.find_all('div', class_="shelf-product-island")
      tries += 1
      
    if tries>1:
      raise RuntimeError("Número de intentos de carga superados")
    
    cheap_item = next(filter(lambda item: item.find('span', class_='out-of-stock') is None,all_items))

    item_name = cheap_item.find('h2', class_="shelf-product-title-text").string
    #item_brand = cheap_item.find('h2', class_="shelf-product-brand").text
    item_price = cheap_item.find('span', class_="price-best").string if cheap_item.find('span',class_="price-best") else cheap_item.find('span', class_="product-sigle-price-wrapper").string
    return {
      'name':item_name,
      'price':format_to_int(item_price)
    }
  
  except Exception as e:
    print(e)
    return {
      'name':'Producto no encontrado',
      'price': 0
    }

async def market_scraper(urls):
    # Initializating session and tasks for each market and their respective urls
    session = AsyncHTMLSession()
    lider_tasks = asyncio.gather(*[lider_scraper(url,session,0) for url in urls['lider']])
    acuenta_tasks = asyncio.gather(*[acuenta_scraper(url,session,3) for url in urls['acuenta']])
    jumbo_tasks = asyncio.gather(*[cencosud_scraper(url, session, 5) for url in urls['jumbo']])
    sisabel_tasks = asyncio.gather(*[cencosud_scraper(url, session, 5) for url in urls['santa_isabel']])

    # Gathering the tasks and await them
    results = await asyncio.gather(lider_tasks,acuenta_tasks,jumbo_tasks,sisabel_tasks)

    sum_lider, sum_acuenta, sum_jumbo, sum_sisabel = total_sum(results[0]), total_sum(results[1]), total_sum(results[2]), total_sum(results[3])

    print(f"Lider total: {sum_lider}\n\n")
    print(f"Acuenta total: {sum_acuenta}\n\n")
    print(f"Jumbo total: {sum_jumbo}\n\n")
    print(f"Santa Isabel total: {sum_sisabel}\n\n")

    final_data = {
        'lider':sum_lider,
        'acuenta':sum_acuenta,
        'jumbo':sum_jumbo,
        'santa_isabel':sum_sisabel
    }

    # Close session and return
    await session.close()
    return f"Most cheap in: {min(final_data, key=final_data.get)}"