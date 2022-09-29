import re
import functools

def format_to_int(str):
    return int(re.sub('[\$,.]','',str.text))

def total_sum(market_list):
    print(market_list)
    prices = [product['price'] for product in market_list if (product is not None)]
    return functools.reduce(lambda a,b: a+b, prices)