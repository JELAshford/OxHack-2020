from nltk.corpus import stopwords
from wordcloud import wordcloud
from wordcloud.wordcloud import WordCloud
from textblob import TextBlob
from collections import Counter
import matplotlib.pylab as plt
import pandas as pd 
import re

# Define project path
PROJ_PATH = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/James_IdeaTesting/TwitterVisualiser/"
PLOT = False

# Read in tweets
search_term = 'Climate Change'
tweet_file = pd.read_csv(f"{PROJ_PATH}rsc/{search_term}_tweets.csv")
tweets = tweet_file["Tweet"].dropna().values

# Extract and clean words
all_words = TextBlob(" ".join(tweets).upper()).words.singularize().lemmatize()
# Get stop-words
stop_words = list(set(stopwords.words('english'))) + ['thi']
# Remove Stop and Short Words
words = [w for w in all_words if len(w) > 2 and w.lower() not in stop_words]

# Convert into one long string
tweet_str = " ".join(words)

# Create word-cloud
word_cloud = WordCloud(font_path=f"{PROJ_PATH}rsc/swiss_911_ultra_compressed_bt.ttf",
                        mode="RGBA", background_color=None, colormap="Blues", 
                        width=1000, height=1000, max_words=2000)
word_cloud.generate(tweet_str)
# Save
save_name = f"{PROJ_PATH}output/{search_term}_wordcloud.png"
word_cloud.to_file(save_name)

# Show in matplotlib
if PLOT:
    plt.figure(figsize=(15, 10))
    plt.imshow(word_cloud) #, interpolation='bilinear')
    plt.axis('off')
    plt.show()


# Get counts of each word
# counts = dict(Counter(words))
# ord_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
# print(ord_counts)