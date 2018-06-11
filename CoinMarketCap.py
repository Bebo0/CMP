import json 
import requests 
import string
import re
from collections import Counter

def getCoinNames():
	""" parses all coins' names and returns them in the form of a list

	"""

	# file  = open("Coins.txt","w")
	result = []
	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=100')
	for coin in r.json():
		strong = str(coin)
		strong = coin["name"].lower() # encode('ascii','ignore')

		# removes spaces in a coin's name
		strong = re.sub('[\s+]', '', strong)

		result.append(strong)
	return result

	file .close()

def getCoinSymbols():
	""" parses all coins' symbols and returns them in the form of a list

	"""
	result = []
	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=100')
	for coin in r.json():
		strong = str(coin)

		strong = coin["symbol"].lower()
		result.append(strong)
	return result



def main():

	getCoins()

if __name__ == '__main__':
	main()