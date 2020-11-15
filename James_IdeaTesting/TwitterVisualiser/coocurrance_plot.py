from collections import Counter
from textblob import TextBlob
import matplotlib as mpl
import matplotlib.pylab as plt
import matplotlib.font_manager as font_manager
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
NUM_OF_COOCS = 10

# Sort out fonts
font_files = font_manager.findSystemFonts(fontpaths=f"{PROJ_PATH}rsc")
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)

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

# Remove words that only occur once
counts = dict(Counter(words))
key_words = [word for word in counts if counts[word] > 1]

# Create dtm
dtm = np.array([[1 if (tweet.upper().count(word) > 0) else 0 for word in key_words] for tweet in tweets])
# Co-occurrances
cooc = np.dot(dtm.T, dtm)

graph_data = []
tier2_names = []
for term in TextBlob(search_term).words:
    # Statistical significance of search_term
    term_dice_stats = dice_significance(cooc, term, key_words)
    term_dice_stats = dict_value_sort(term_dice_stats)
    # Get NUM_OF_COOCS most similar words
    most_similar = list(term_dice_stats.keys())[0:NUM_OF_COOCS]
    tier2_names += most_similar
    # Create a structure to hold the node links
    graph_data += [{"from":term.upper(), "to":set_name, "stat":term_dice_stats[set_name]} for set_name in most_similar]
    # Iterate over each of the chosen coocs, and find their closest
    for word in most_similar:
        # Find stats for this word
        word_dice_stats = dice_significance(cooc, word, key_words)
        word_dice_stats = dict_value_sort(word_dice_stats)
        # Choose top nearby matches
        top_neighbours = list(word_dice_stats.keys())[0:10]
        new_graph_data = [{"from":word.upper(), "to":set_name, "stat":word_dice_stats[set_name]} for set_name in top_neighbours]
        # Add to existing graph data
        graph_data += new_graph_data

# Convert graph data to pandas dataframe
gd = pd.DataFrame.from_dict(graph_data)
# Create co-occurance graph
# G = nx.from_numpy_matrix(cooc)
G = nx.from_pandas_edgelist(gd, "from", "to", "stat")
pos = nx.nx_agraph.graphviz_layout(G, prog='fdp')

# Generate colours
colours, sizes = [], []
for node in G:
    if node in TextBlob(search_term).words.upper():
        col = 'red'
        size = 2000
    elif node in tier2_names:
        col = 'orange'
        size = 500
    else:
        col = 'blue'
        size = 100
    colours.append(col)
    sizes.append(size)

# Visualisation
fig = plt.figure(figsize=(15, 10))
nx.draw_networkx(G, pos, with_labels=True, alpha=0.5, node_color=colours, node_size = sizes, font_family="Swiss911 UCm BT", font_size=18)
nx.draw_networkx_labels(G, pos, font_family="Swiss911 UCm BT", font_size=18)

# Save
save_name = f"{PROJ_PATH}output/{search_term}_coocgraph.png"
plt.savefig(save_name, dpi=300)

# Show
plt.show()