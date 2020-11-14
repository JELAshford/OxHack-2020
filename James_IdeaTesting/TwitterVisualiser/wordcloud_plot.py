import re
import pandas as pd 
import matplotlib.pylab as plt
from wordcloud import wordcloud
from wordcloud.wordcloud import WordCloud
from collections import Counter

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