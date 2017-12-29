import praw

def authenticate():
	""" Logs us into Reddit and returns an object which allows us to interact with Reddit's API

	void -> Reddit
	"""
	print "Authenticating"
	reddit = praw.Reddit('wordcounterbot',
			user_agent = "Bebo's Word Counter")
	print "Successfully authenticated as {}".format(reddit.user.me())
	return reddit