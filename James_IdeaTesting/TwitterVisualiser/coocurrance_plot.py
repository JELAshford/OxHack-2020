from collections import Counter
import matplotlib.pylab as plt
import pandas as pd 

# Define project path
PROJ_PATH = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/James_IdeaTesting/TwitterVisualiser/"
PLOT = False

# Read in tweets
search_term = 'Trump'
tweet_file = pd.read_csv(f"{PROJ_PATH}rsc/{search_term}_tweets.csv")
tweets = tweet_file["Tweet"].dropna().values

# Remove short words 
all_words = " ".join(tweets).upper().split(" ")
words = [w for w in all_words if len(w) > 4]
# Convert into one long string
tweet_str = " ".join(words)