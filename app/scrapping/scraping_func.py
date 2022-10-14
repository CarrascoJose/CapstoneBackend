import asyncio
from bs4 import BeautifulSoup
import requests_html
from requests_html import AsyncHTMLSession

import time
import functools
import re
from .utils import format_to_int, total_sum



async def fetch_html(url:str, session:AsyncHTMLSession, sleep: int):
    # Async coroutine to fetch and render the pages
    try:
        r = await session.get(url)
        print(f"Response received of: {url}")
        if sleep>0:
            await r.html.arender(sleep=sleep,timeout=30)
        print(f"Rendered: {url}")
        return r
    except Exception as e:
        raise Exception(e.message)

def get_soup(r):
    # Block of code to get the html and parse
    html = r.html.raw_html
    soup = BeautifulSoup(html,'lxml')
    return soup 


async def lider_scraper(url: str, amount: int , session: AsyncHTMLSession, sleep: int):
    # Async coroutine to implement the lider web scraper
    try:
        r = await fetch_html(url, session, sleep)
        soup = get_soup(r)
        product_name = soup.find('span',class_='product-description')
        price = soup.find('span',class_='price-sell')

        tries = 0

        while ((product_name is None) or (price is None)) and tries<=1:
            print(f"Reintentando...{url}")
            r = await fetch_html(url, session, sleep)
            soup = get_soup(r)
            product_name = soup.find('span',class_='product-description')
            price = soup.find('span',class_='price-sell')
            tries+=1

        if tries>1:
            raise RuntimeError("Número de intentos de carga superados")

        return {
            'name':product_name.string,
            'price':format_to_int(price.string)*amount
        }

    except Exception as e:
        print(e)
        return {
            'name':"Producto no encontrado",
            'price':0
        }

async def acuenta_scraper(url: str, amount: int, session: AsyncHTMLSession, sleep: int):
    # Async coroutine to implement the acuenta web scraper
    try:
        r = await fetch_html(url, session, sleep)
        soup = get_soup(r)
        prices = soup.find_all('p',class_='sc-jAaTju')
        #print(soup)
        tries = 0
        while len(prices)<1 and tries<=1:
            print("Reintentando...")
            r = await fetch_html(url, session, sleep)
            soup = get_soup(r)
            prices = soup.find_all('p',class_='sc-jAaTju')
            tries+=1
        
        if tries>1:
            raise RuntimeError("Número de intentos de carga superados")

        min_price_tag = functools.reduce(lambda a,b: a if int(re.sub('[\$,.]','',a.string)) < int(re.sub('[\$,.]','',b.text)) else b, prices)

        min_price = min_price_tag.string
        product_name = min_price_tag.parent.find("p",class_="prod__name").span.string

        return {
            'name':product_name,
            'price':format_to_int(min_price)*amount
        }    

    except Exception as e:
        print(e)
        return {
            'name':"Producto no encontrado",
            'price':0
        }

async def cencosud_scraper(url: str, amount: int, session: AsyncHTMLSession, sleep: int):
  try:
    r = await fetch_html(url, session, sleep)
    soup = get_soup(r)
    all_items = soup.find_all('div', class_="shelf-product-island")

    tries = 0
    while len(all_items)<1 and tries<2:
      print("Reintentando...Jumbo...")
      r = await fetch_html(url, session, sleep)
      soup = get_soup(r)
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
      'price':format_to_int(item_price) * amount
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

    # Running separate tasks
    lider = await asyncio.gather(*[lider_scraper(item["url"],item["amount"],session,0) for item in urls['lider']])
    acuenta = await asyncio.gather(*[acuenta_scraper(item["url"],item["amount"],session,5) for item in urls['acuenta']])
    jumbo = await asyncio.gather(*[cencosud_scraper(item["url"],item["amount"],session,3) for item in urls['jumbo']])
    ssisabel = await asyncio.gather(*[cencosud_scraper(item["url"],item["amount"],session,3) for item in urls['santa_isabel']])

    sum_lider, sum_acuenta, sum_jumbo, sum_sisabel = total_sum(lider), total_sum(acuenta), total_sum(jumbo), total_sum(ssisabel)

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
    return min(final_data, key=final_data.get)#f"Most cheap in: {min(final_data, key=final_data.get)}"