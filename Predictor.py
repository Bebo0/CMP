import praw 
import string
import re
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
		self.counter = Counter()
		self.karmaCounter = Counter()
		#self.rankingScore = 0



    # FUNCTIONS:
	def addOccurenceAndKarmaToCounters(self, aos, karma):
		""" Adds the occurence of all strings in given array to counter

		ArrayOfStrings -> void

		Arguments:
			aos {ArrayOfStrings} -- contains all the words to be added to counter
		"""

		for word in aos:
			if word in self.counter:
				self.counter[word] += 1
				self.karmaCounter[word] += karma
			else:
				self.counter[word] = 1
				self.karmaCounter[word] += karma

	def addKarmaToCounter(self, aos):
		""" Adds karma score of every string to karmaCounter

		ArrayOfStrings -> void

		Arguments:
			aos {ArrayOfStrings} -- contains all the words to be added to counter
		"""

		for word in aos:
			if word in self.counter:
				self.counter[word] += 1
			else:
				self.counter[word] = 1


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

			self.parsingHelper(strong, comment.score)
		print "Successfully parsed comments!"


	def parsingHelper(self, strong, karma):
		""" Splits strong into individual strings then adds them to the counter 
		
		"""
		allowedSymbols = string.letters + string.digits + ' ' + '\'' + '-'
		aos = re.sub('[^%s]' % allowedSymbols,'',strong)
		aos = aos.split()
		self.addOccurenceAndKarmaToCounters(aos, karma)


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
			self.parsingHelper(strong, post.score)
			#print post.score
			#print comment.downs

		print "Successfully parsed post titles!"


	def runBot(self, reddit):
		""" Parses comments and titles
		Reddit -> void

		Parses the comments and/or titles in the given subreddit, and adds the occurence of certain strings found to counter.
			
		Arguments:
			reddit {Reddit} -- [the Reddit object that allows us to interact with Reddit's API]
		"""
		#parseComments(reddit)
		self.parsePostTitles(reddit)


def main():

	bot = Predictor('cryptocurrency')
	bot.runBot(Predictor.reddit)
	print bot.karmaCounter

if __name__ == '__main__':
	main()