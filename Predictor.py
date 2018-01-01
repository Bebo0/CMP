import praw 
import string
import re
import math
import sys
import inspect
import time
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
	

	def __init__(self, subredditname, dateInitial, dateEnd):
		"""constructs a Predictor object
		
		Arguments:
			subredditname {string} -- the subreddit being parsed
		"""
		self.subRedditName = subredditname
		self.counter       = Counter()
		self.karmaCounter  = Counter()
		self.ranking       = Counter() 
		self.ranking2      = Counter()
		self.dateInitial = dateInitial
		self.dateEnd     = dateEnd


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
				self.rankingAlgorithm(word, karma, time)
			else:
				self.counter[word]        = 1
				self.karmaCounter[word]   = karma
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
			
			
			#print post.score
			#print comment.downs

		print "Successfully parsed post titles!"

	def rankingAlgorithm(self, word, karma, time):
		""" ranks a word that appears in the counters depending on karma and how early the word's post was submitted on Reddit
		
		This algorithm is a modified version of Reddit's algorithm that ensures posts on the front page stay "fresh" but also "interesting".
		More info here: http://scienceblogs.com/builtonfacts/2013/01/16/the-mathematics-of-reddit-rankings-or-how-upvotes-are-time-travel/

		The modification in my algorithm stems from the fact that Reddit's algorithm ranks posts. My program ranks the words
		in posts, so there's an extra layer of difficulty; the same word can appear in multiple posts. Therefore, my algorithm
		ranks words depending on 3 factors: karma garnered, the number of occurences, and the time posted.

		First, this algorithm takes the halfway point between the difference between initial and end dates
		to later assign a value to the word's posted time. 
		Example: initalDate = now, endDate = 24 hours ago. Halfway between would be 12 hours ago.
		We find the halfway point because that is when an average post would be submitted. 

		A word that appears in a post submitted 24 hours ago gains 0 points.
		A word that appears in a post submitted 12 hours ago gains 1 point. 
		A word that appears in a post submitted 0  hours ago gains 2 points.

		The second part of the algorithm deals with karma; the more karma the word's post garners, the higher thr word's score.
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
		halfwayBetweenInitialEnd = (self.dateEnd - self.dateInitial)/2
		if karma > 0:
			self.ranking[word] += (2 - ((time - self.dateInitial)/halfwayBetweenInitialEnd)) + math.log(karma, 10)
		else:
			self.ranking[word] += (2 - ((time - self.dateInitial)/halfwayBetweenInitialEnd))


	def rankingAlgorithm2(self):
		""" this is a simpler algorithm that ranks words depending on their upvote:occurence ratio

		"""
		for key in self.counter:
			self.ranking2[key] = self.karmaCounter[key]/self.counter[key]


	def runBot(self, reddit):
		""" Parses comments and titles
		Reddit -> void

		Parses the comments and/or titles in the given subreddit, and adds the occurence of certain strings found to counter.
			
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		#parseComments(reddit)
		self.parsePostTitles(reddit)
		self.rankingAlgorithm2()
		self.printRankings()

	def printRankings(self):
		""" writes out the ranked words to a file named Rankings
		
		"""
		file  = open("Rankings1.txt","w")
		file2 = open("Rankings2.txt","w")

		file .write(repr(self.ranking) + '\n' )
		file2.write(repr(self.ranking2) + '\n' )



		file .close()
		file2.close()

def main():

	bot = Predictor('cryptocurrency', Predictor.TIME_24HOURS_AGO, Predictor.TIME_NOW)
	bot.runBot(Predictor.REDDIT)

if __name__ == '__main__':
	main()

