import praw 
import string
import re
import math
import pickle
from collections import Counter
from Authenticator import authenticate

# USAGE: 
#        1) download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html 
#        2) in terminal, cd to folder which contains project files
#        3) type python Predictor.py

class Predictor:

	reddit = authenticate() #authenticate called here so that only 1 authentication occurs even if multiple objects are instantiated

	# CONSTRUCTOR:
	def __init__(self, subredditname):
		"""constructs a Predictor object
		
		Arguments:
			subredditname {string} -- the subreddit being parsed
		"""
		self.subRedditName = subredditname
		self.counter       = Counter()
		self.karmaCounter  = Counter()
		self.ranking       = Counter() 
		self.aggregateTime = Counter()
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
				self.rankingAlgorithm(word)
			else:
				self.counter[word]       = 1
				self.karmaCounter[word]  = karma
				self.aggregateTime[word] = time
				self.rankingAlgorithm(word)


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
		dateInitial = 1514507792 #1514453887 #1514078600 is December 25th, 2017 9:10pm PST. Convert time to UNIX time here: https://www.unixtimestamp.com/
		dateEnd     = 1514535992 #1514507792   #1514265000 is December 26th, 2017 9:10pm PST

		for post in reddit.subreddit(self.subRedditName).submissions(dateInitial, dateEnd):

			strong = ''.join(post.title).lower().encode('ascii','ignore')
			self.parsingHelper(strong, post.score, post.created_utc)
			#print post.score
			#print comment.downs

		print "Successfully parsed post titles!"

	def rankingAlgorithm(self, word):
		""" ranks all words that appear in the counters depending on karma and how early the post was submitted on Reddit

			
		Arguments:
			aggregateTime {Integer} -- the aggregate time of the submission of all the word's occurences
		"""
		if self.karmaCounter[word] > 0:
			self.ranking[word] += round((math.log10(self.karmaCounter[word]) + self.aggregateTime[word]/(1500000000*self.counter[word])), 2)
		else:
			self.ranking[word] += round(self.aggregateTime[word]/(1500000000*self.counter[word]), 2)

		



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
		file.write( 'dict = ' + repr(self.ranking) + '\n' )
			#file.write('\n'.join(self.ranking[key]))
			#file.write(key)


		file.close()



def main():

	bot = Predictor('cryptocurrency')
	bot.runBot(Predictor.reddit)
	bot.printRankings()
	#print bot.ranking

if __name__ == '__main__':
	main()