import praw 
import string
import re
import math
import sys
import inspect
import time
import operator
import CoinMarketCap
import requests
import json
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
from Authenticator import authenticate
from datetime import datetime



""" 
Usage:
    1) Download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html.
	2) Download matplotlib. Follow instruction here: https://matplotlib.org/users/installing.html
    3) (optional) Specifiy subRedditsToParse, endDate and startDate in the initializer variable in main inside predictor.py.
	4) (optional) Specifiy which ranking to plot (self.ranking, self.ranking2, self.sentimentRanking) in the self.plotRankings() call in main inside predictor.py
    5) In terminal, cd to folder which contains project files.
    6) Type python predictor.py.
    7) Look at results in plotted graph. Full data also available in the rawdata.json file.

The sentiment analyzer used in this program is a modified version of the VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment anaylzer.

"""


class Predictor:

	REDDIT = authenticate() # authenticate called here so that only 1 authentication occurs even if multiple objects are instantiated
	TIME_NOW         = int(time.time()) # epoch (UTC) time
	TIME_24HOURS_AGO = int(time.time()) - 86400
	TIME_7DAYS_AGO   = int(time.time()) - 86400*7


	def __init__(self, subredditsToParse, startDate, endDate):
		"""constructs a Predictor object
		
		Arguments:
			subredditsToParse {ArrayOfStrings} -- the subreddits being parsed
			startDate         {Integer}        -- the start date of parsing
			endDate           {Integer}        -- the end date of parsing
		"""
		self.subredditsToParse   = subredditsToParse
		self.subRedditName       = ""
		self.counter             = Counter() # word counter
		self.karmaCounter        = Counter()
		self.ranking             = Counter() 
		self.ranking2            = Counter()
		self.sentimentRanking    = Counter()
		self.symbolName          = Counter()
		self.startDate           = startDate # in epoch (UTC) time
		self.endDate             = endDate
		self.coinNames           = []
		self.coinSymbols         = []
		self.analyzer            = SentimentIntensityAnalyzer()


    # FUNCTIONS:
	def addScores(self, aos, karma, time, sentiment):
		""" Adds the mentions, karma, and sentiment scores of all strings in given array to counters

		Arguments:
			aos       {ArrayOfStrings} -- contains all the words (cryptocurrency names or symbols) to be added to counters
			karma     {Integer}        -- the karma score of the post/comment containing  the coin's name or symbol
			time      {Integer}        -- the time posted of the post/comment containing  the coin's name or symbol
			sentiment {Integer}        -- the sentiment score of the post/comment containing  the coin's name or symbol
		"""
		wsf = []
		for word in aos:
			# filters words so that only cryptocurrency names or symbols will be added to counter
			
			if word in self.coinNames and (word not in wsf):
				wsf.append(word)
				self.counter[word]      += 1
				self.karmaCounter[word] += karma
				self.rankingAlgorithm(word, karma, time)
				if karma <= 0:
					self.sentimentRanking[word] += sentiment
				else:
					self.sentimentRanking[word] += sentiment*(1+(math.log(karma, 10)))

			elif (word in self.coinSymbols) and (self.symbolName[word] not in wsf):
				wsf.append(self.symbolName[word])
				self.counter[self.symbolName[word]]      += 1
				self.karmaCounter[self.symbolName[word]] += karma
				self.rankingAlgorithm(self.symbolName[word], karma, time)
				if karma <= 0:
					self.sentimentRanking[self.symbolName[word]] += sentiment
				else:
					self.sentimentRanking[self.symbolName[word]] += sentiment*(1+(math.log(karma, 10)))
				

			


	def authenticate():
		""" Logs us into Reddit and returns an object which allows us to interact with Reddit's API

		"""
		print("Authenticating")
		reddit = praw.Reddit('wordcounterbot',
				user_agent = "Bebo's Word Counter")
		print("Successfully authenticated as {}".format(reddit.user.me()))
		return reddit

	def createjson(self):
		""" Outputs raw data to rawdata.json

		"""

		json_results = []
		# creates a sorted version of the counter dictionary in the form of a list of tuples.
		sortedDictionary = sorted(list(self.counter.items()), key=lambda x: x[1], reverse=True)
		
		for t in sortedDictionary:

			obj = {}
			obj['karma'] = self.karmaCounter[t[0]]
			obj['mentions'] = t[1]
			obj['score1'] = self.ranking[t[0]]
			obj['score2'] = self.ranking2[t[0]]
			obj['coinname'] = t[0]
			obj['sentiment'] = self.sentimentRanking[t[0]]
			
			json_results.append(obj)
			
		with open("RawData.json", "w") as jsonFile:
			json.dump(json_results, jsonFile)


	def getCoins(self):
		""" gets all coins' names and symbols and initializes symbolName[]
		
		"""

		self.coinNames   = CoinMarketCap.getCoinNames()
		self.coinSymbols = CoinMarketCap.getCoinSymbols()

		if len(self.coinNames) != len(self.coinSymbols):
			raise Exception('Some coin has no symbol. Parse less coins')

		for x in range(0,len(self.coinNames)):
			self.symbolName[self.coinSymbols[x]] = self.coinNames[x]



	def parseComments(self, reddit, x):
		""" Parses the first x number of comments that appear in a subreddit
		
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		
		print("Parsing comments in /r/"+str(self.subRedditName)+"...")
		
		for comment in reddit.subreddit(self.subRedditName).comments(limit=x):

			# transforms all letters of the comment body to lowercase
			body = ''.join(comment.body).lower()

			self.parsingHelper(body, comment.score, comment.created_utc)


		print ("Successfully parsed comments!")


	def parsingHelper(self, body, karma, time):
		""" Splits body into individual strings then adds mention/karma/sentiment scores to the ranking counters 
		
		"""
		allowedSymbols = string.ascii_letters + string.digits + ' ' + '\'' + '-'
		aos = re.sub('[^%s]' % allowedSymbols,'',body)
		aos = aos.split()

		# Sentiment analyzer score for whole post/comment
		vs = self.sentimentAlgorithm(body)
		# we add the normalized, weighted composite score ("compound") of the whole post/comment to the scores
		self.addScores(aos, karma, time, vs.get("compound", 0) )


	def parsePostTitles(self, reddit):
		""" Parses all post titles from startDate to endDate in the given subreddit
		
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		print("Parsing post titles in /r/"+str(self.subRedditName)+"...")

		data = self.getPushshiftData(self.startDate, self.endDate, self.subRedditName)


		for submission in data:
			strong = ''.join(submission["title"]).lower()
			vs = self.analyzer.polarity_scores(strong)
			self.parsingHelper(strong, submission["score"], submission["created_utc"])

		print("Successfully parsed post titles!")
	

	def getPushshiftData(self, after, before, sub):
		url = 'https://api.pushshift.io/reddit/search/submission?&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(self.subRedditName)
		r = requests.get(url)
		data = json.loads(r.text)
		return data['data']



	def plotRankings(self, n, r):
		""" Plots the top n coins 
		
		Arguments:
			n {int}  -- [number of coin rankings to be plotted]
			r {dict} -- [dictionary rankings to be plotted]
		"""
		sortedRankings = sorted(list(r.items()), key=lambda x: x[1], reverse=True)
		tempList = []

		if (n>len(r)):
			n = len(r)
		for x in range(1,n):
			tempList.append(sortedRankings[x])
	
		x_axisCoinNames  = list(zip(*tempList))[0]
		y_axisCoinScores = list(zip(*tempList))[1]

		mpl_fig = plt.figure()
		ax = mpl_fig.add_subplot(111)
		ax.bar(list(range(len(tempList))), y_axisCoinScores, 0.5, align='center', color='skyblue') 
		# ax.grid() 
		ax.set_title('Rankings')
		plt.xticks(list(range(len(tempList))), x_axisCoinNames, size='small')
		plt.show()

	def rankingAlgorithm(self, word, karma, time):
		""" custom algorithm that ranks a word that appears in the counters depending on karma and how early the word's post was submitted on Reddit
	
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


	def ratioAlgorithm(self):
		""" upvote:mentions algorithm

		"""
		for key in self.counter:
			self.ranking2[key] = self.karmaCounter[key]/self.counter[key]

	def sentimentAlgorithm(self, body):

		""" returns sentiment score of body

		
		For a comprehensive explanation of how sentiment scores are calculated, go to 
		Cryptocurrency-Market-Predictor\vaderSentiment\vaderSentiment\vaderSentiment.py,
		starting at line 520. Source of algorithm: https://github.com/cjhutto/vaderSentiment

		"""
		return self.analyzer.polarity_scores(body)
		



	def runBot(self, reddit):

		self.getCoins()
		for subreddit in self.subredditsToParse:
			self.subRedditName = subreddit
			self.parseComments(reddit, 1000)
			self.parsePostTitles(reddit)

		self.ratioAlgorithm()
		self.plotRankings(20, self.sentimentRanking)

		

def main():
	subredditsToParse = ['cryptocurrency' , 'cryptomarkets', 'bitcoinmarkets', 'cryptotechnology']# , 'altcoin']
	bot = Predictor(subredditsToParse, Predictor.TIME_24HOURS_AGO, Predictor.TIME_NOW)
	bot.runBot(Predictor.REDDIT)
	bot.createjson()


if __name__ == '__main__':
	main()

