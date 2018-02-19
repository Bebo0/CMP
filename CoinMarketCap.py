import json 
import requests 
import string
from collections import Counter

def getCoins():
	""" parses all coins' names and symbols and writes them to Coins.txt

	"""

	file  = open("Coins.txt","w")
	
	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=2000')
	for coin in r.json():
		strong = ''.join(coin["name"]).lower().encode('ascii','ignore')
		strong1 = ''.join(coin["symbol"]).lower().encode('ascii','ignore')

		file .write(repr(strong) )
		file .write(repr(strong1) + '\n' )

	file .close()


def main():

	getCoins()

if __name__ == '__main__':
	main()




# def getCoins():
# 	testArr = []
	
# 	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=2000')
# 	for coin in r.json():
# 		test = Counter()
# 		test[coin["name"].lower()] = coin["symbol"].lower()

# 		testArr.append(test)
# 	    #print(coin["name"].lower())
# 	    #print(coin["symbol"].lower())
# 	    #print("\n")
# 	print(testArr)