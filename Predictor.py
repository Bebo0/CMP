import praw 
import string
import re
import math
import sys
import inspect
import time
import operator
import CoinMarketCap
import pandas as pd
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from Authenticator import authenticate
from datetime import datetime



"""
Usage:
1) Download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html.
2) Specifiy subRedditsToParse, endDate and startDate in the initializer variable in the main function in Predictor.py.
3) In terminal, cd to folder which contains project files.
4) Type python Predictor.py.
5) Look at results in plotted graph. Data also available in the rawdata.json file.
"""

class Predictor:

	REDDIT = authenticate() # authenticate called here so that only 1 authentication occurs even if multiple objects are instantiated
	TIME_NOW         = int(time.time()) # epoch (UTC) time
	TIME_24HOURS_AGO = int(time.time()) - 86400/2
	TIME_7DAYS_AGO   = int(time.time()) - 86400*7


	def __init__(self, subredditsToParse, startDate, endDate):
		"""constructs a Predictor object
		
		Arguments:
			subredditname {String}  -- the subreddit being parsed
			startDate     {Integer} -- the start date of parsing
			endDate       {Integer} -- the end date of parsing
		"""
		self.subredditsToParse = subredditsToParse
		self.subRedditName = subredditsToParse[0]
		self.counter       = Counter() # word counter
		self.karmaCounter  = Counter()
		self.ranking       = Counter() 
		self.ranking2      = Counter()
		self.nameSymbols   = Counter()
		self.startDate     = startDate # in epoch (UTC) time
		self.endDate       = endDate
		self.coinNames     = []

    # FUNCTIONS:
	def addScores(self, aos, karma, time):
		""" Adds the occurence and karma scores of all strings in given array to counters

		Arguments:
			aos   {ArrayOfStrings} -- contains all the words to be added to counters
			karma {Integer}        -- the karma score
			time  {Integer}        -- the time posted
		"""
		for word in aos:
			if self.filter(word):
				self.counter[word]      += 1
				self.karmaCounter[word] += karma
				self.rankingAlgorithm(word, karma, time)
			


	def authenticate():
		""" Logs us into Reddit and returns an object which allows us to interact with Reddit's API

		"""
		print "Authenticating"
		reddit = praw.Reddit('wordcounterbot',
				user_agent = "Bebo's Word Counter")
		print "Successfully authenticated as {}".format(reddit.user.me())
		return reddit

	def createjson(self):
		""" Outputs raw data to rawdata.json

		"""

		json_results = []
		# creates a sorted version of the counter dictionary in the form of a list of tuples.
		sortedDictionary = sorted(self.counter.items(), key=lambda x: x[1], reverse=True)
		
		for t in sortedDictionary:

			obj = {}
			obj['karma'] = self.karmaCounter[t[0]]
			obj['mentions'] = t[1]
			obj['score1'] = self.ranking[t[0]]
			obj['score2'] = self.ranking2[t[0]]
			obj['coinname'] = t[0]
			
			json_results.append(obj)
			
		with open("RawData.json", "w") as jsonFile:
			json.dump(json_results, jsonFile)



	def filter(self, word):
		""" checks if the given word is a coin name or symbol
		
		Arguments:
			word {String} -- the word to be checked
		"""

		if word in self.coinNames:
			return True

		else:
			return False


	def getCoins(self):
		""" gets all coins' names and symbols from Coins.txt
		
		"""
		with open('Coins.txt','r') as f:
			for line in f:
				c = 0

		 		for word in line.split():
		 			word = word.strip('\'"') 
	
					self.coinNames.append(word)
		
			
		


	def parseComments(self, reddit, x):
		""" Parses the first x number of comments that appear in a subreddit
		
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		
		print "Parsing comments in /r/"+str(self.subRedditName)+"..."
		
		for comment in reddit.subreddit(self.subRedditName).comments(limit=x):

			# transforms all letters of the comment body to lowercase and transforms the comment from unicode 
			# to ascii for easier readability
			strong = ''.join(comment.body).lower().encode('ascii','ignore')

			self.parsingHelper(strong, comment.score, comment.created_utc)

		print "Successfully parsed comments!"


	def parsingHelper(self, strong, karma, time):
		""" Splits strong into individual strings then adds them to the counter 
		
		"""
		allowedSymbols = string.letters + string.digits + ' ' + '\'' + '-'
		aos = re.sub('[^%s]' % allowedSymbols,'',strong)
		aos = aos.split()
		 
		self.addScores(aos, karma, time)


	def parsePostTitles(self, reddit):
		""" Parses all post titles from startDate to endDate in the given subreddit
		
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		print "Parsing post titles in /r/"+str(self.subRedditName)+"..."

		data = self.getPushshiftData(self.startDate, self.endDate, self.subRedditName)

		for submission in data:
			strong = ''.join(submission["title"]).lower().encode('ascii','ignore')
			self.parsingHelper(strong, submission["score"], submission["created_utc"])

		print "Successfully parsed post titles!"
	

	def getPushshiftData(self, after, before, sub):
		url = 'https://api.pushshift.io/reddit/search/submission?&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(self.subRedditName)
		r = requests.get(url)
		data = json.loads(r.text)
		return data['data']



	def plotRankings(self, n):
		""" Plots the top n coins 
		
		Arguments:
			n {int} -- [number of coin rankings to be plotted]
		"""
		sortedRankings = sorted(self.ranking.items(), key=lambda x: x[1], reverse=True)
		tempList = []

		if (n>len(self.ranking)):
			n = len(self.ranking)
		for x in xrange(1,n):
			tempList.append(sortedRankings[x])
	
		x_axisCoinNames  = zip(*tempList)[0]
		y_axisCoinScores = zip(*tempList)[1]

		mpl_fig = plt.figure()
		ax = mpl_fig.add_subplot(111)
		ax.bar(range(len(tempList)), y_axisCoinScores, 0.5, align='center', color='skyblue') 
		# ax.grid() 
		ax.set_title('Rankings')
		plt.xticks(range(len(tempList)), x_axisCoinNames, size='small')
		plt.show()

	def rankingAlgorithm(self, word, karma, time):
		""" ranks a word that appears in the counters depending on karma and how early the word's post was submitted on Reddit
	
		This algorithm is a modified version of Reddit's algorithm that ensures posts on the front page stay "fresh" but also "interesting".
		More info here: http://scienceblogs.com/builtonfacts/2013/01/16/the-mathematics-of-reddit-rankings-or-how-upvotes-are-time-travel/

		The modification in my algorithm stems from the fact that Reddit's algorithm ranks posts; my program ranks the words
		in posts. My algorithm ranks words depending on 3 aspects of their posts: karma garnered, the number of occurences, and the time posted.

		First, this algorithm takes the halfway point between the difference between initial and end dates
		to later assign a value to the word's posted time. 
		Example: initalDate = now, endDate = 24 hours ago. Halfway between would be 12 hours ago.
		We find the halfway point because that is when an "average" post would be submitted. 

		A word that appears in a post submitted 24 hours ago gains 0 points.
		A word that appears in a post submitted 12 hours ago gains 1 point. 
		A word that appears in a post submitted 0  hours ago gains 2 points.

		The second part of the algorithm deals with karma; the more karma the word's post garners, the higher the word's score.
		I'm assuming Reddit's algorithm uses (log10 of karma) because the average post garners close to 10 upvotes. 
		On /r/cryptocurrency, the average post garners 30 upvotes, BUT the median is much lower. I kept it at log10 of karma
		to place more importance on karma. 

		Example of algorithm:
		The word 'bitcoin' appeared in a post submitted 12 hours ago with 1000 upvotes.
		The word 'bitcoin' gains (2-1)+log10(1000) = 1 + 3 = 4 points

		The word 'ethereum' appeared in a post submitted 0 hours ago with 0 upvotes.
		The word 'ethereum' gains (2-0) = 2 = 2 points

		The word 'dogecoin' appeared in a post submitted 24 hours ago with 0 upvotes.
		The word 'dogecoin' gains (2-2) = 0 = 0 points


		Arguments:
			word  {String}  -- the word being ranked
			karma {Integer} -- the word's post's karma
			time  {Integer} -- the word's post's time submitted
		"""
		halfwayBetween = (self.endDate - self.startDate)/2
		if karma > 0:
			self.ranking[word] += (2 - ((time - self.startDate)/halfwayBetween)) + math.log(karma, 10)
		else:
			self.ranking[word] += (2 - ((time - self.startDate)/halfwayBetween))


	def rankingAlgorithm2(self):
		""" this is a seperate, simpler algorithm that ranks words depending on their upvote:occurence ratio

		"""
		for key in self.counter:
			self.ranking2[key] = self.karmaCounter[key]/self.counter[key]


	def runBot(self, reddit):
		""" Parses comments and titles

		Parses the comments and/or titles in the given subreddit, and adds the occurence of
		certain strings found to counter.
			
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		CoinMarketCap.getCoins()
		self.getCoins()
		for subreddit in self.subredditsToParse:
			self.subRedditName = subreddit
			self.parseComments(reddit, 2000)
			self.parsePostTitles(reddit)

		
		self.rankingAlgorithm2()
		self.plotRankings(20)
		

def main():
	subredditsToParse = ['cryptocurrency', 'cryptomarkets', 'bitcoinmarkets', 'cryptotechnology', 'altcoin']
	bot = Predictor(subredditsToParse, Predictor.TIME_24HOURS_AGO, Predictor.TIME_NOW)
	bot.runBot(Predictor.REDDIT)
	bot.createjson()


if __name__ == '__main__':
	main()

