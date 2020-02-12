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

current_year_awards = []
yearly_tweets = []
award_mapping = {}
found_nominees = {}

# spacy stuff
nlp_client = spacy.load('en_core_web_sm')
nlp_tokenizer = Tokenizer(nlp_client.vocab)
tweet_tokenizer = helpers.TweetTokenizer(nlp_client, nlp_tokenizer)

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
    tweet_handler = helpers.TweetHandler()
    host_tweets = tweet_handler.get_host_tweets(yearly_tweets)

    imdb_handler = helpers.IMDBHandler()
    names = imdb_handler.get_names(host_tweets, use_imdb_database=False)
    hosts = tweet_handler.get_most_common_names(names, variance=50)
    print(hosts)
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    global award_mapping
    tweet_handler = helpers.TweetHandler()
    awards_tweets = tweet_handler.get_awards_tweets(yearly_tweets)
    awards = tweet_handler.process_awards_tweets(yearly_tweets, awards_tweets, nlp_client, current_year_awards)
    award_mapping = awards
    # todo: split awards from awards mapping
    return awards

def get_nominees(year):
    """Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.
    """


def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    official_awards = OFFICIAL_AWARDS_1315 if int(year) in [2013, 2015] else OFFICIAL_AWARDS_1819

    found_presenters = {}
    presenter_pattern = re.compile('present[^a][\w]*\s([\w]+\s){1,5}')

    for award in official_awards:
        for tweet in yearly_tweets:
            for a in award_mapping[award]:
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
    global yearly_tweets, current_year_awards
    year = '2013' # todo
    current_year_awards = OFFICIAL_AWARDS_1315 if int(year) in [2013, 2015] else OFFICIAL_AWARDS_1819
    yearly_tweets = get_tweets_from_file(year)

    # todo: move this, maybe into nominations?
    # add awards to tokenizer
    tweet_tokenizer.add_tokens_from_awards(current_year_awards)
    tweet_tokenizer.add_tokens_from_keywords()

    get_hosts(year)
    get_awards(year)
    return

if __name__ == '__main__':
    main()
