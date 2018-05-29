# Cryptocurrency-Market-Predictor
A program that predicts the crypto market using Reddit.


# Usage
        1) download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html.
        2) in terminal, cd to folder which contains project files.
        3) type python Predictor.py.
        4) look at results in Rankings.txt and Rankings2.txt.


# How it works:
1) User specifies a subreddit dateEnd and dateStart in the initializer variable in the main function in Predictor.py. Example: bot = Predictor('cryptocurrency', Predictor.TIME_24HOURS_AGO, Predictor.TIME_NOW).
2) The program parses the posts and/or comments in the given subreddit, and filters cryptocurrency projects' names and symbols.
3) An algorithm then ranks cryptocurrencies by how frequently they are mentioned in posts and/or comments, how many upvotes the posts or comments garner, and how soon they were posted on Reddit.
4) A bar grap is plotted of the results when the program ends. Also, raw results are outputted to rankings.txt and rankings2.txt.


# Update May 28th
PRAW no longer supports parsing post titles. Therefore, the program as is can only parse comments. This will be fixed soon.

