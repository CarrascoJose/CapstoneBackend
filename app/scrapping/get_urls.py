


# Get urls from each market given the basket passed by the user
def get_lider_urls(basket):
    return [
        {
            "url": f'https://www.lider.cl/supermercado/search?Ns=sku.internetPrice%7C0&Ntt={product["prod"]}',
            "amount":product["amount"]
        }
        for product in basket]

def get_acuenta_urls(basket):
    return [
        {
            "url":f'https://www.acuenta.cl/search?name={product["prod"]}',
            "amount":product["amount"]
        }
        for product in basket]

def get_jumbo_urls(basket):
  return [
        {
            "url":"https://www.jumbo.cl/busqueda?ft="+product["prod"].replace(' ', '%20')+"&o=OrderByPriceASC&page=1",
            "amount":product["amount"]
        }
        for product in basket]

def get_sisabel_urls(basket):
  return [
        {
            "url":"https://www.santaisabel.cl/busqueda?ft="+product["prod"].replace(' ', '%20')+"&o=OrderByPriceASC&page=1",
            "amount":product["amount"]
        }
        for product in basket]
######################