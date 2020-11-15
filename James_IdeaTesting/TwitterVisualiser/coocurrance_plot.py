from collections import Counter
from textblob import TextBlob
import matplotlib.pylab as plt
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
import networkx as nx

def dict_value_sort(dictionary):
    return(dict(sorted(dictionary.items(), key=lambda item: item[1], reverse=True)))

def dice_significance(cooc_array, word, word_list):
    """Dice statistical significance for "word" against all
    other words in "word_list" using corresponding 2d array
    of cooccurrance.
    """
    word_index = word_list.index(word.upper())
    k = len(cooc_array)
    ki = sum(cooc_array[:, word_index])
    kj = np.sum(cooc_array, axis=0)
    kij = cooc_array[word_index, :]
    dice_stat = 2 * kij / (ki + kj)
    stat_dict = {word: d for word, d in zip(word_list, dice_stat)}
    stat_dict.pop(word.upper())
    return(stat_dict)

# Define project path
PROJ_PATH = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/James_IdeaTesting/TwitterVisualiser/"
NUM_OF_COOCS = 5

# Read in tweets
search_term = 'Trump'
tweet_file = pd.read_csv(f"{PROJ_PATH}rsc/{search_term}_tweets.csv")
tweets = tweet_file["Tweet"].dropna().values

# Extract and clean words
all_words = TextBlob(" ".join(tweets).upper()).words.singularize().lemmatize()
# Get stop-words
stop_words = list(set(stopwords.words('english')))
# Remove Stop and Short Words
words = [w for w in all_words if len(w) > 2 and w.lower() not in stop_words]

# Remove words that only occur once
counts = dict(Counter(words))
key_words = [word for word in counts if counts[word] > 1]

# Create dtm
dtm = np.array([[1 if (tweet.upper().count(word) > 0) else 0 for word in key_words] for tweet in tweets])
# Co-occurrances
cooc = np.dot(dtm.T, dtm)

# Statistical significance of search_term
search_term_dice_stats = dice_significance(cooc, search_term, key_words)
search_term_dice_stats = dict_value_sort(search_term_dice_stats)

# Get NUM_OF_COOCS most similar words
most_similar = list(search_term_dice_stats.keys())[0:NUM_OF_COOCS]

# Create a structure to hold the node links
graph_data = [{"from":search_term.upper(), "to":set_name, "stat":search_term_dice_stats[set_name]} for set_name in most_similar]

# Iterate over each of the choseon coocs, and find their closest
for word in most_similar:
    # Find stats for this word
    word_dice_stats = dice_significance(cooc, word, key_words)
    word_dice_stats = dict_value_sort(word_dice_stats)
    # Choose top 20 nearby matches
    top_neighbours = list(word_dice_stats.keys())[0:10]
    new_graph_data = [{"from":word.upper(), "to":set_name, "stat":word_dice_stats[set_name]} for set_name in top_neighbours]
    # Add to existing graph data
    graph_data += new_graph_data

# Convert graph data to pandas dataframe
gd = pd.DataFrame.from_dict(graph_data)

# Create co-occurance graph
# G = nx.from_numpy_matrix(cooc)
G = nx.from_pandas_edgelist(gd, "from", "to", "stat")
# pos = nx.spring_layout(G, k=0.42, iterations=17)
# pos = nx.kamada_kawai_layout(G)

# Visualisation
fig = plt.figure()
nx.draw_networkx(G, with_labels=True, node_size=100, alpha=0.8, cmap="Blues")
plt.show()