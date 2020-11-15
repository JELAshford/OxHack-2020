from nltk.corpus import stopwords

import matplotlib.pylab as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates

from wordcloud import wordcloud
from wordcloud.wordcloud import WordCloud

from textblob import TextBlob

import pandas as pd
import numpy as np

import tweepy

from collections import Counter
import sys, re
import datetime

import networkx as nx

def generate_csv(keyword, save_path):

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

    # Search API
    public_tweets = api.search(keyword, count=100, result_type='recent')

    # Generate list of tuples: (tweet, polarity, subjectivity)
    tweet_data = []
    # Set the initial date and iterate thorugh the tweets for the past 7 days
    day_num = 1
    update_date = datetime.datetime.now() + datetime.timedelta(days=1)
    until_date = str(update_date).split(" ")[0]
    while day_num <= 7:

        # Search the api for this keyword up until here
        public_tweets = api.search(keyword, count=100, result_type='recent',until=until_date)
        
        for tweet in public_tweets:
            # Remove emoji from text
            twt = tweet.text.translate(emoji_begone)
            # Filter out links
            twt = re.sub(r"http\S+", "", twt)
            # Remove RT prefix
            twt = re.sub("(RT\s@.*:\s)", "", twt).strip()
            # Remove twitter handles
            twt = re.sub("(@.*\s)", "", twt)
            # Correct ampersand
            twt = re.sub("(&amp;)", "&", twt)
            # Replace newlines and underscores
            twt = re.sub("[(\\n)(_)(-)(\/)]", " ", twt)
            # Replace special characters
            twt = re.sub("['`…’.£#\*\"\@\!\?]", "", twt)

            # Polarity/Subj Analysis
            ps_analysis = TextBlob(twt)
            pol = ps_analysis.sentiment.polarity
            subj = ps_analysis.sentiment.subjectivity
            time = str(tweet.created_at).split(" ")[0]

            tweet_summary = (twt, pol, subj, time)
            tweet_data.append(tweet_summary)
        
        #Update the date
        update_date = update_date-datetime.timedelta(days=1)
        until_date = str(update_date).split(" ")[0]
        day_num += 1
    
    # Keep only unique results
    print(f"Got {len(tweet_data)} tweets overall on '{keyword}'")
    tweet_data = list(set(tweet_data))
    print(f"Got {len(tweet_data)} unique tweets on '{keyword}'")

    # Convert to pandas dataframe and save
    file_path = f"{save_path}/{keyword}_tweets.csv"
    saved_tweets = pd.DataFrame(tweet_data)
    saved_tweets.columns = ["Tweet", "Polarity", "Subjectivity", "Time"]
    saved_tweets.to_csv(file_path, header=True, index=False)

    return saved_tweets


def wordcloud_plot(search_term, tweets_dataframe, save_path):

    tweets = tweets_dataframe["Tweet"].dropna().values

    # Extract and clean words
    all_words = TextBlob(" ".join(tweets).upper()).words.lemmatize()
    # Get stop-words
    stop_words = list(set(stopwords.words('english'))) + ['thi']
    # Remove Stop and Short Words
    words = [w for w in all_words if len(w) > 2 and w.lower() not in stop_words]

    # Convert into one long string
    tweet_str = " ".join(words)

    # Create word-cloud
    word_cloud = WordCloud(font_path="/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/Interface/rsc/swiss_911_ultra_compressed_bt.ttf",
                            mode="RGBA", background_color=None, colormap="Blues", 
                            width=1000, height=600, max_words=2000)
    word_cloud.generate(tweet_str)
    # Save
    file_name = f"{save_path}/{search_term}_wordcloud.png"
    word_cloud.to_file(file_name)

    return True


def cooc_graph(search_term, tweets_dataframe, save_path, NUM_OF_COOCS=5):

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

    ALL_SEARCH_TERMS = TextBlob(search_term).words
    
    tweets = tweets_dataframe["Tweet"].dropna().values

    # Sort out fonts
    font_files = font_manager.findSystemFonts(fontpaths="/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/Interface/rsc")
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)

    # Extract and clean words
    all_words = TextBlob(" ".join(tweets).upper()).words.lemmatize()
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
            size = min(counts[node]*100, 5000) #5000
            l0[node] = node
        elif node in layer1_names:
            col = 'lightblue' #'orange'
            size = min(counts[node]*100, 3000) #2500
            l1[node] = node
        else:
            col = 'cyan' #'blue'
            size = counts[node]*10 #1000
            l2[node] = node
        colours.append(col)
        sizes.append(size)

    # Visualisation
    fig = plt.figure(figsize=(5, 3), dpi=200)
    pos = nx.spring_layout(G)
    if len(ALL_SEARCH_TERMS) == 1:
        pos = nx.nx_agraph.graphviz_layout(G, prog='twopi')
    # Draw edges
    edges = nx.draw_networkx_edges(G, pos, alpha=1, width=1, edge_color='white') #width=gd["stat"].values*10)
    # Draw nodes, once white for background then again with colour+alpha
    nodes = nx.draw_networkx_nodes(G, pos, alpha=1, node_color='white', node_size=sizes)
    nodes = nx.draw_networkx_nodes(G, pos, alpha=0.8, node_color=colours, node_size=sizes)
    nodes.set_edgecolor('black')
    # Draw labels for each layer, with proportional sizes
    labels0 = nx.draw_networkx_labels(G, pos, labels=l0, font_family="Swiss911 UCm BT", font_size=30)
    labels1 = nx.draw_networkx_labels(G, pos, labels=l1, font_family="Swiss911 UCm BT", font_size=15)
    labels2 = nx.draw_networkx_labels(G, pos, labels=l2, font_family="Swiss911 UCm BT", font_size=11, font_color="white")
    labels2 = nx.draw_networkx_labels(G, pos, labels=l2, font_family="Swiss911 UCm BT", font_size=10, font_color="black")

    # Save
    file_name = f"{save_path}/{search_term}_coocgraph.png"
    plt.savefig(file_name, transparent=True)


def ps_graph(search_term, tweets_dataframe, save_path):

    # Sort out fonts
    font_files = font_manager.findSystemFonts(fontpaths="/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/Interface/rsc")
    font_list = font_manager.createFontList(font_files)
    font_manager.fontManager.ttflist.extend(font_list)
    from matplotlib import rcParams
    rcParams['font.family'] = "Swiss911 UCm BT"
    rcParams['font.size'] = 18
    
    # Extract data from tweets_dataframe
    pols = tweets_dataframe["Polarity"].values
    subjs = tweets_dataframe["Subjectivity"].values
    times = tweets_dataframe["Time"].values

    # Convert times to mdates datetimes
    tweet_datetimes = [mdates.date2num(datetime.datetime.strptime(t, "%Y-%m-%d")) for t in times]

    # Scatterplot coloured by datetime
    fig = plt.figure(figsize=(5, 3), dpi=200)
    ax = fig.add_subplot(111)
    sc = ax.scatter(pols, subjs, c=tweet_datetimes)

    # Create colourbar with autoformatted mdates
    loc = mdates.AutoDateLocator()
    cbar = fig.colorbar(sc, ticks=loc, format=mdates.AutoDateFormatter(loc))

    # Make all the axes white for viewing
    ax.tick_params(axis='x', colors="white")
    ax.tick_params(axis='y', colors="white")
    ax.set_xlabel("Polarity", color='white')
    ax.set_ylabel("Subjectivity", color='white')
    ax.spines['top'].set_edgecolor('white')
    ax.spines['bottom'].set_edgecolor('white')
    ax.spines['left'].set_edgecolor('white')
    ax.spines['right'].set_edgecolor('white')
    cbar.ax.tick_params(axis='y', colors='white')
    [t.set_color('white') for t in cbar.ax.xaxis.get_ticklabels()]
    [t.set_color('white') for t in cbar.ax.yaxis.get_ticklabels()]

    # Save
    file_name = f"{save_path}/{search_term}_psplot.png"
    plt.savefig(file_name, transparent=True, pad_inches=0, bbox_inches='tight')

    return True

def generate_plots(keyword, save_path = "/Users/jamesashford/Documents/Projects/Hackathons/Oxford Hack 2020/OxHack-2020/Interface/output"):

    # Generate .csv of tweet data from keyword
    tweet_df = generate_csv(keyword, save_path)

    # Draw the wordcloud
    wordcloud_plot(keyword, tweet_df, save_path)

    # Draw the Cooc graph
    cooc_graph(keyword, tweet_df, save_path)

    # Draw the PS Graph
    ps_graph(keyword, tweet_df, save_path)
