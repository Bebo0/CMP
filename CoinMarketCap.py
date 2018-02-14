import json 
import requests 
import string
from collections import Counter

def getCoins():
	# testArr = []

	file  = open("Coins.txt","w")
	# file2 = open("Rankings2.txt","w")

	# file .write(repr(self.ranking) + '\n' )
	# file2.write(repr(self.ranking2) + '\n' )

	
	# file2.close()
	
	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=2000')
	for coin in r.json():
		# test = Counter()
		strong = ''.join(coin["name"]).lower().encode('ascii','ignore')
		strong1 = ''.join(coin["symbol"]).lower().encode('ascii','ignore')

		file .write(repr(strong) )
		file .write(repr(strong1) + '\n' )

		# test[strong] = strong1

		# testArr.append(test)
	    #print(coin["name"].lower())
	    #print(coin["symbol"].lower())
	    #print("\n")
	    #
	file .close()
	# print(testArr)


def main():

	
	#test["bitcoin"] = "btc"
	#print(test)
	getCoins()

if __name__ == '__main__':
	main()




def getCoins():
	testArr = []
	
	r = requests.get('https://api.coinmarketcap.com/v1/ticker/?limit=2000')
	for coin in r.json():
		test = Counter()
		test[coin["name"].lower()] = coin["symbol"].lower()

		testArr.append(test)
	    #print(coin["name"].lower())
	    #print(coin["symbol"].lower())
	    #print("\n")
	print(testArr)