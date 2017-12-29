class ParsedWord:

	reddit = authenticate() #authenticate called here so that only 1 authentication occurs even if multiple objects are instantiated

	# CONSTRUCTOR:
	def __init__(self, subredditname):