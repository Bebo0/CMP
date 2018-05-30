# Cryptocurrency-Market-Predictor
A program that predicts the crypto market using Reddit.


# Usage:
        1) Download PRAW. Follow instructions here: http://praw.readthedocs.io/en/latest/getting_started/installation.html.
        2) Specifiy subRedditsToParse, endDate and startDate in the initializer variable in the main function in Predictor.py.
        3) In terminal, cd to folder which contains project files.
        4) Type python Predictor.py.
        5) Look at results in plotted graph. Data also available in the rawdata.json file.


# How it works:
        1) The program parses the posts and/or comments between dateStart and dateEnd in the given subreddits.
        2) Program filters cryptocurrency projects' names and symbols from the posts and comments and keeps track of number of mentions, karma, and time posted.
        3) An algorithm then ranks cryptocurrencies by how frequently they are mentioned in posts and/or comments, how many upvotes the posts or comments garner, and how soon they were posted on Reddit.
        4) A bar grap is plotted of the results using matplotlib when the program ends. Also, raw results are outputted to rawdata.json.

