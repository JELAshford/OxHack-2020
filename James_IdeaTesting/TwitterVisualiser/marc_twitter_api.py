from textblob import TextBlob
import pandas as pd
import sys, re
import tweepy

# Character map to remove enojis
emoji_begone = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

# Neccessary API keys
keys = pd.read_csv("/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/access_keys.csv").columns
consumer_key = keys[0]
consumer_secret = keys[1]
access_token = keys[2]
access_token_secret = keys[3]

# Authorise access and create API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Make public search
search_term = 'Climate Change'
public_tweets = api.search(search_term, count=100, result_type='recent')

# Generate list of tuples: (tweet, polarity, subjectivity)
tweet_data = []
for tweet in public_tweets:
    # Remove emoji from text
    twt = tweet.text.translate(emoji_begone)
    # Filter out links
    twt = re.sub(r"http\S+", "", twt)
    # Remove RT prefix
    twt = re.sub("(RT\s@.*:\s)", "", twt).strip()
    # Correct ampersand
    twt = re.sub("(&amp;)", "&", twt)
    # Replace newlines and underscores
    twt = re.sub("[(\\n)(_)(-)(\/)]", " ", twt)
    # Replace special characters
    twt = re.sub("['`…’.£#\*\"@!?]", "", twt)

    analysis = TextBlob(twt)
    pol = analysis.sentiment.polarity
    subj = analysis.sentiment.subjectivity

    tweet_summary = (twt, pol, subj)
    tweet_data.append(tweet_summary)

print(len(tweet_data))
# Convert to pandas dataframe and save
rsc_path = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/James_IdeaTesting/TwitterVisualiser/rsc"
save_path = f"{rsc_path}/{search_term}_tweets.csv"
saved_tweets = pd.DataFrame(tweet_data)
saved_tweets.to_csv(save_path, header=["Tweet", "Polarity", "Subjectivity"], index=False)
