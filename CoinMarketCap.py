import json 
import requests 
import string

r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=2000')
for coin in r.json():
    print(coin["name"].lower())
    print(coin["symbol"].lower())
    #print("\n")