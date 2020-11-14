from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

import pandas as pd 

# Read in tweets
tweet_file = pd.read_csv("/Users/jamesashford/Documents/Projects/Hackathons/IdeaTesting/ZoomSentimentAnalysis/rsc/MeToo_tweets.csv")
tweets = tweet_file["Text"].values[1:20]

for tweet in tweets:
    blob_object = TextBlob(tweet, analyzer=NaiveBayesAnalyzer())
    analysis = blob_object.sentiment
    print(f"Tweet: {tweet}")
    print(f"Analysis: {analysis}")
    print("")