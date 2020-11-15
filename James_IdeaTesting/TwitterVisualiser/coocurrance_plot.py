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
SEARCH_TERM = 'Climate Change'
ALL_SEARCH_TERMS = TextBlob(SEARCH_TERM).words

# Sort out fonts
font_files = font_manager.findSystemFonts(fontpaths=f"{PROJ_PATH}rsc")
font_list = font_manager.createFontList(font_files)
font_manager.fontManager.ttflist.extend(font_list)

# Read in tweets
tweet_file = pd.read_csv(f"{PROJ_PATH}rsc/{SEARCH_TERM}_tweets.csv")
tweets = tweet_file["Tweet"].dropna().values

# Extract and clean words
all_words = TextBlob(" ".join(tweets).upper()).words.singularize().lemmatize()
# Get stop-words
stop_words = list(set(stopwords.words('english'))) + ['thi']
# Remove Stop and Short Words
words = [w for w in all_words if len(w) > 3 and w.lower() not in stop_words]

# Remove words that only occur once
counts = dict(Counter(words))
key_words = [word for word in counts if counts[word] > 1]

# Create dtm
dtm = np.array([[1 if (tweet.upper().count(word) > 0) else 0 for word in key_words] for tweet in tweets])
# Co-occurrances
cooc = np.dot(dtm.T, dtm)

graph_data = []
layer1_names = []
layer2_names = []
for term in ALL_SEARCH_TERMS:
    # Statistical significance of search_term
    term_dice_stats = dice_significance(cooc, term, key_words)
    term_dice_stats = dict_value_sort(term_dice_stats)
    # Get NUM_OF_COOCS most similar words
    most_similar = list(term_dice_stats.keys())[0:NUM_OF_COOCS]
    layer1_names += most_similar
    # Create a structure to hold the node links
    graph_data += [{"from":term.upper(), "to":set_name, "stat":term_dice_stats[set_name]} for set_name in most_similar]
    # Iterate over each of the chosen coocs, and find their closest
    for word in most_similar:
        # Find stats for this word
        word_dice_stats = dice_significance(cooc, word, key_words)
        word_dice_stats = dict_value_sort(word_dice_stats)
        # Choose top nearby matches
        top_neighbours = list(word_dice_stats.keys())[0:10]
        layer2_names += top_neighbours
        new_graph_data = [{"from":word.upper(), "to":set_name, "stat":word_dice_stats[set_name]} for set_name in top_neighbours]
        # Add to existing graph data
        graph_data += new_graph_data

# Convert graph data to pandas dataframe
gd = pd.DataFrame.from_dict(graph_data)
# Create co-occurance graph
# G = nx.from_numpy_matrix(cooc)
G = nx.from_pandas_edgelist(gd, "from", "to", "stat")

# Generate colours
colours, sizes = [], []
l0, l1, l2 = {}, {}, {}
for node in G:
    if node in ALL_SEARCH_TERMS.upper():
        col = 'darkblue' #'red'
        size = counts[node]*1000 #5000
        l0[node] = node
    elif node in layer1_names:
        col = 'lightblue' #'orange'
        size = counts[node]*1000 #2500
        l1[node] = node
    else:
        col = 'cyan' #'blue'
        size = counts[node]*100 #1000
        l2[node] = node
    colours.append(col)
    sizes.append(size)

# Visualisation
fig = plt.figure(figsize=(15, 10))
pos = nx.spring_layout(G)
if len(ALL_SEARCH_TERMS) == 1:
    pos = nx.nx_agraph.graphviz_layout(G, prog='twopi')
# Draw edges
edges = nx.draw_networkx_edges(G, pos, alpha=1, width=2, edge_color='white') #width=gd["stat"].values*10)
# Draw nodes, once white for background then again with colour+alpha
nodes = nx.draw_networkx_nodes(G, pos, alpha=1, node_color='white', node_size=sizes)
nodes = nx.draw_networkx_nodes(G, pos, alpha=0.8, node_color=colours, node_size=sizes)
nodes.set_edgecolor('black')
# Draw labels for each layer, with proportional sizes
labels0 = nx.draw_networkx_labels(G, pos, labels=l0, font_family="Swiss911 UCm BT", font_size=60)
labels1 = nx.draw_networkx_labels(G, pos, labels=l1, font_family="Swiss911 UCm BT", font_size=30)
labels2 = nx.draw_networkx_labels(G, pos, labels=l2, font_family="Swiss911 UCm BT", font_size=22, font_color="white")
labels2 = nx.draw_networkx_labels(G, pos, labels=l2, font_family="Swiss911 UCm BT", font_size=21, font_color="black")

# Save
save_name = f"{PROJ_PATH}output/{SEARCH_TERM}_coocgraph.png"
plt.savefig(save_name, dpi=300, transparent=True)

# Show
plt.show()