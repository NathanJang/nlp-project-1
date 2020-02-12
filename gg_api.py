'''Version 0.35'''

import helpers
import json
import spacy
from spacy.tokenizer import Tokenizer
import en_core_web_sm
from collections import Counter
import re


OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

# TODO: CHANGE VARIABLE NAMES (maybe move into dict?)
CURRENT_YEAR_OFFICIAL_AWARDS = []
YEARLY_TWEETS = []
AWARD_MAPPING = {}
__predicted_nominees = {}

# dictionary with all of our located values
RESULTS = {}

# spacy stuff
nlp_client = spacy.load('en_core_web_sm')
nlp_tokenizer = Tokenizer(nlp_client.vocab)

# class handlers
tweet_tokenizer = helpers.TweetTokenizer(nlp_client, nlp_tokenizer)
imdb_handler = helpers.IMDBHandler()
tweet_handler = helpers.TweetHandler()


def get_tweets_from_file(year):
    '''Parses a json file of tweets to extract tweet text data.

    :param year: int, year
    :return: array of tweet text content
    '''
    with open(f'gg{year}.json', 'r') as tweet_file:
        tweets_data = json.load(tweet_file)
        return [tweet.get('text') for tweet in tweets_data]


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    global RESULTS
    host_tweets = tweet_handler.get_host_tweets(YEARLY_TWEETS)
    names = imdb_handler.get_names(host_tweets, use_imdb_database=False)
    hosts = tweet_handler.get_most_common_names(names, variance=50)
    print(hosts)
    RESULTS['hosts'] = hosts
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    global AWARD_MAPPING
    tweet_handler = helpers.TweetHandler()
    awards_tweets = tweet_handler.get_awards_tweets(YEARLY_TWEETS)
    awards = tweet_handler.process_awards_tweets(YEARLY_TWEETS, awards_tweets, nlp_client, CURRENT_YEAR_OFFICIAL_AWARDS)
    AWARD_MAPPING = awards
    # todo: split awards from awards mapping
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    global __predicted_nominees
    nominees = {}
    stopwords = ['winner', 'this year', 'could win', 'tonight', 'next year\'s', 'next year', 'http', '@', 'rt', 'tweet', 'twitter']
    tweet_handler = helpers.TweetHandler()
    award_mapping = tweet_handler.process_awards_tweets([], YEARLY_TWEETS, nlp_client, CURRENT_YEAR_OFFICIAL_AWARDS)
    for award in CURRENT_YEAR_OFFICIAL_AWARDS:
        print("Searching for nominees for award %s in year %s" % (award, year))
        # if award needs a person as a result (actor/actress/director/etc)
        type_of_award = ""
        cut = 0.15
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            type_of_award = "name"
            cut = 0.3
        # reduce to tweets about the desired award
        relevant_tweets = []
        for tweet in YEARLY_TWEETS:
            adder = False
            for match in award_mapping[award]:
                if match.lower() in tweet.lower() or match.lower()[0:int(len(match.lower()) / 2)] in tweet.lower():
                    adder = True
            if adder:
                relevant_tweets.append(tweet)
        potential_nominees = {}
        uncleaned_dict = {}
        if type_of_award == "name":
            uncleaned_dict = nlp_tokenizer(relevant_tweets, 'PERSON', year)
        else:
            uncleaned_dict = nlp_tokenizer(relevant_tweets, 'WORK_OF_ART', year)

        for item in uncleaned_dict:
            adding = True
            for word in stopwords:
                # if __is_similar(word, item.lower()) > 0.75 or item.lower() in word or word in item.lower():
                #     adding = False
            adding = not tweet_handler.fuzzy_list_includes(stopwords, item) # do not add if item is in stopwords
            if adding:
                # k = __val_exists_in_keys(potential_nominees, item)
                if not tweet_handler.fuzzy_list_includes(potential_nominees, item):
                    if (type_of_award != 'name' and item not in imdb_handler.names) or (type_of_award == 'name' and item in imdb_handler.names):
                        potential_nominees[item] = uncleaned_dict[item]
                else:
                    potential_nominees[k] += uncleaned_dict[item]
        c = Counter(potential_nominees)

        # Cutoff:
        nom_counts = c.most_common(len(c))
        if potential_nominees:  # if we have potential noms
            max = nom_counts[0][1]  # get the max mentions for nom
            noms = []
            for potential_nom in nom_counts:
                if potential_nom[1] > (cut * max):  # cutoff is different for people vs movie awards, see above
                    noms.append(potential_nom[0])
            if len(noms) > 0:
                nominees[award] = noms
            else:
                nominees[award] = ['no one']  # want to scrap this line
        else:
            nominees[award] = ["_nom_"]
    __predicted_nominees = nominees
    return nominees


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    global RESULTS
    winners = {}
    for award in CURRENT_YEAR_OFFICIAL_AWARDS:
        winners[award] = __predicted_nominees[award][0]
    RESULTS['winners'] = winners
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    official_awards = OFFICIAL_AWARDS_1315 if int(year) in [2013, 2015] else OFFICIAL_AWARDS_1819

    found_presenters = {}
    presenter_pattern = re.compile('present[^a][\w]*\s([\w]+\s){1,5}')

    for award in official_awards:
        for tweet in YEARLY_TWEETS:
            for a in AWARD_MAPPING[award]:
                match = None
                if a.lower() in tweet.lower():
                    match = presenter_pattern.search(tweet)

    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    global YEARLY_TWEETS, CURRENT_YEAR_OFFICIAL_AWARDS
    year = '2013' # todo
    CURRENT_YEAR_OFFICIAL_AWARDS = OFFICIAL_AWARDS_1315 if int(year) in [2013, 2015] else OFFICIAL_AWARDS_1819
    YEARLY_TWEETS = get_tweets_from_file(year)

    # todo: move this, maybe into nominations?
    # add awards to tokenizer
    tweet_tokenizer.add_tokens_from_awards(CURRENT_YEAR_OFFICIAL_AWARDS)
    tweet_tokenizer.add_tokens_from_keywords()

    get_hosts(year)
    get_awards(year)
    return

if __name__ == '__main__':
    main()
