# Cryptocurrency-Market-Predictor
A program that predicts the crypto market using Reddit.


# Usage:
        1) Download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html.
	2) Download matplotlib. Follow instruction here: https://matplotlib.org/users/installing.html
        3) (optional) Specifiy subRedditsToParse, endDate and startDate in the initializer variable in main inside predictor.py.
	4) (optional) Specifiy which ranking to plot (self.ranking, self.ranking2, self.sentimentRanking) in the self.plotRankings() call in main inside predictor.py
        5) In terminal, cd to folder which contains project files.
        6) Type python predictor.py.
        7) Look at results in plotted graph. Full data also available in the rawdata.json file.


# How it works:
        1) The program parses the posts and/or comments between dateStart and dateEnd in the given subreddits.
        2) Program filters cryptocurrency names and symbols from the posts and comments and keeps track of number of mentions, karma, time posted. Program also assigns a sentiment score to each cryptocurrency.
        3) 3 different algorithms (a sentiment analyzer algorithim, a custom algorithm , an upvote:mention ratio algorithm) rank the cryptocurrencies.
        4) When the program ends, a bar grap of the results is plotted using matplotlib. Also, raw results are outputted to rawdata.json.

