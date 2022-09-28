import re


async def formatToInt(str):
    return int(re.sub('[\$,.]','',str.text))