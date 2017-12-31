import praw 
import string
import re
import math
import pickle
import sys
import inspect
import time
from decimal import Decimal
from collections import Counter
from Authenticator import authenticate
from datetime import datetime

# USAGE: 
#        1) download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html 
#        2) in terminal, cd to folder which contains project files
#        3) type python Predictor.py

class Predictor:

	REDDIT = authenticate() #authenticate called here so that only 1 authentication occurs even if multiple objects are instantiated
	TIME_NOW         = int(time.time()) # epoch (UTC) time
	TIME_24HOURS_AGO = int(time.time()) - 86400
	AVG_UPVOTE_TO_POST_RATIO = 30
	ARB_DATE = 1104537600
	# CONSTRUCTOR:
	def __init__(self, subredditname, dateInitial, dateEnd):
		"""constructs a Predictor object
		
		Arguments:
			subredditname {string} -- the subreddit being parsed
		"""
		self.subRedditName = subredditname
		self.counter       = Counter()
		self.karmaCounter  = Counter()
		self.ranking       = Counter() 
		self.aggregateTime = Counter()
		self.dateInitial = dateInitial
		self.dateEnd     = dateEnd
		self.amountOfPosts = 0
		self.amountOfUpvotes = 0
		#self.rankingScore = 0



    # FUNCTIONS:
	def addOccurenceAndKarmaToCounters(self, aos, karma, time):
		""" Adds the occurence and karma of all strings in given array to counters

		ArrayOfStrings Integer -> void

		Arguments:
			aos   {ArrayOfStrings} -- contains all the words to be added to counters
			karma {Integer}        -- the karma score
		"""

		for word in aos:
			if word in self.counter:
				self.counter[word]       += 1
				self.karmaCounter[word]  += karma
				self.aggregateTime[word] += time
				self.rankingAlgorithm(word, karma, time)
			else:
				self.counter[word]       = 1
				self.karmaCounter[word]  = karma
				self.aggregateTime[word] = time
				self.rankingAlgorithm(word, karma, time)


	def authenticate():
		""" Logs us into Reddit and returns an object which allows us to interact with Reddit's API

		void -> Reddit
		"""
		print "Authenticating"
		reddit = praw.Reddit('wordcounterbot',
				user_agent = "Bebo's Word Counter")
		print "Successfully authenticated as {}".format(reddit.user.me())
		return reddit


	def parseComments(self, reddit):
		""" Parses the first x number of comments that appear in a subreddit

		Reddit -> void
		
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		
		print "Parsing comments..."
		x = 1000
		for comment in reddit.subreddit(self.subRedditName).comments(limit=x):

			# transforms all letters of the comment body to lowercase and transforms the comment from unicode to ascii for easier readability
			strong = ''.join(comment.body).lower().encode('ascii','ignore')

			self.parsingHelper(strong, comment.score, comment.created_utc)
		print "Successfully parsed comments!"


	def parsingHelper(self, strong, karma, time):
		""" Splits strong into individual strings then adds them to the counter 
		
		"""
		allowedSymbols = string.letters + string.digits + ' ' + '\'' + '-'
		aos = re.sub('[^%s]' % allowedSymbols,'',strong)
		aos = aos.split()
		self.addOccurenceAndKarmaToCounters(aos, karma, time)


	def parsePostTitles(self, reddit):
		""" Parses all post titles from dateInitial to dateEnd in the given subreddit

		Reddit -> void
		
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		
		print "Parsing post titles..."
		#dateInitial = 1514078600 #1514535992 #1514453887 #1514078600 is December 25th, 2017 9:10pm PST. Convert time to UNIX time here: https://www.unixtimestamp.com/
		#dateEnd     = 1514265000 #1514621677  #1514507792   #1514265000 is December 26th, 2017 9:10pm PST

		for post in reddit.subreddit(self.subRedditName).submissions(self.dateInitial, self.dateEnd):

			strong = ''.join(post.title).lower().encode('ascii','ignore')
			self.parsingHelper(strong, post.score, post.created_utc)
			self.amountOfPosts +=1
			self.amountOfUpvotes += post.score
			#print post.score
			#print comment.downs

		print "Successfully parsed post titles!"

	def rankingAlgorithm(self, word, karma, time):
		""" ranks a word that appears in the counters depending on karma and how early the word's post was submitted on Reddit
		
		This algorithm is an improved version of Reddit's algorithm that ensures posts on the front page stay "fresh" but also "interesting".
		More info here: http://scienceblogs.com/builtonfacts/2013/01/16/the-mathematics-of-reddit-rankings-or-how-upvotes-are-time-travel/


			
		Arguments:
			word {String} -- the word being ranked
		"""
		#postToUpvoteRatio = self.amountOfPosts/self.amountOfUpvotes
		halfwayBetweenInitialEnd = (self.dateEnd - self.dateInitial)/2
		if karma > 0:
			self.ranking[word] += (2 - ((time - self.dateInitial)/halfwayBetweenInitialEnd)) + math.log(karma, Predictor.AVG_UPVOTE_TO_POST_RATIO)
		else:
			self.ranking[word] += (2 - ((time - self.dateInitial)/halfwayBetweenInitialEnd))

		#float(str(round(answer, 2)))

		



	def runBot(self, reddit):
		""" Parses comments and titles
		Reddit -> void

		Parses the comments and/or titles in the given subreddit, and adds the occurence of certain strings found to counter.
			
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		#parseComments(reddit)
		self.parsePostTitles(reddit)

	def printRankings(self):
		""" writes out the ranked words to a file named Rankings
		
		"""
		file = open("Rankings.txt","w") 
		#for key in self.ranking:
			#print "1"
		#pickle.dump(self.ranking, file)
		#self.write_vars_to_file(self.ranking)
		file.write(repr(self.ranking) + '\n' )
		# source = inspect.getsourcelines(inspect.getmodule(inspect.stack()[0][0]))[0]
		# print [x for x in source if x.startswith("mydict = ")]
		
		#file.write(self.ranking)
			#file.write(key)


		file.close()

	# def write_vars_to_file(self, _f, **vars):
	#     for (name, val) in vars.items():
	#         _f.write("%s = %s\n" % (name, repr(val)))





def main():

	bot = Predictor('cryptocurrency', Predictor.TIME_24HOURS_AGO, Predictor.TIME_NOW)
	bot.runBot(Predictor.REDDIT)
	#print Predictor.TIME_NOW
	#print bot.amountOfPosts
	#print bot.amountOfUpvotes
	#print bot.karmaCounter
	bot.printRankings()
	#print bot.ranking

if __name__ == '__main__':
	main()

