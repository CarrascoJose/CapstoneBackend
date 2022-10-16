import re
import functools
import statistics

def format_to_int(str):
    return int(re.sub('[\$,.]','',str.text))

def total_sum(market_list):
    prices = [product['price'] for product in market_list if (product is not None)]
    return functools.reduce(lambda a,b: a+b, prices)

def check_miss_values(markets):
    # Replace the products with price 0 with the mean of the prices on the other markets
    zip_list = list(zip(*markets))
    
    for i,x in enumerate(zip_list):
        prices_mean = statistics.mean([el["price"] for el in x if el["price"]>0])
        
        zip_list[i] = tuple(
            {
            "name":el["name"],
            "price":prices_mean,
            "product":el["product_searched"]
            } if el["price"]==0
            else el 
            for el in x)

    return list(zip(*zip_list))