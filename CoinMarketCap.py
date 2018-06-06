import json 
import requests 
import string
import re
from collections import Counter

def getCoins():
	""" parses all coins' names and symbols and writes them to Coins.txt

	"""

	file  = open("Coins.txt","w")
	
	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=100')
	for coin in r.json():
		strong = str(coin)
		strong = coin["name"].lower() # encode('ascii','ignore')

		# removes spaces in a coin's name
		strong = re.sub('[\s+]', '', strong)
		strong1 = coin["symbol"].lower().encode('ascii','ignore')

		file .write(repr(strong) + ' ')
		file .write(repr(strong1) + '\n' )

	file .close()


def main():

	getCoins()

if __name__ == '__main__':
	main()