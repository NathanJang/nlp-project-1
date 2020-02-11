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

yearly_tweets = []

# spacy stuff
nlp_client = spacy.load('en_core_web_sm')
nlp_tokenizer = Tokenizer(nlp_client.vocab)

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
    official_awards = OFFICIAL_AWARDS_1315 if int(year) in [2013, 2015] else OFFICIAL_AWARDS_1819
    tweet_handler = helpers.TweetHandler()
    awards_tweets = tweet_handler.get_awards_tweets(yearly_tweets)
    # most_common_awards_2 = tweet_handler.get_awards_tweets2(yearly_tweets)
    awards = tweet_handler.process_awards_tweets(yearly_tweets, awards_tweets, nlp_client, official_awards)
    # Your code here
    return []

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    award_to_nominee_mapping = { award: [] for award in awards }
    awards = OFFICIAL_AWARDS_1315 if year == '2013' or year == '2015' else OFFICIAL_AWARDS_1819
    nomination_keywords = set(['nominates', 'nominating', 'nominees', 'nominee', 'nominated'])
    stopwords = set(['grammy', 'though', 'someone', 'however', 'life', 'a', 'magazine', 'film', 'so', 'hooraysupporting', 'best', 'tmz', 'people', 'picture', 'although', 'tune', 'she', 'because', 'eating', 'that', 'newz', 'all', 'vanityfair', 'anyway', 'actress', 'interesting', 'score', 'comedy', 'yay', 'netflix', 'cbs', 'fashion', 'not', 'the', 'and', 'oscars', 'better', 'how', 'cnn', 'he', 'has', 'music', 'oscar', 'mc', 'movie', 'good', 'season', 'congrats', 'television', 'nshowbiz', 'song', 'drinking', 'actor', 'mejor', 'drink', 'drama', 'this', 'fair', 'hooray', 'should'])

    # filter tweets relevant to nominations
    nomination_tweets = [
        tweet
        for tweet in get_tweets_from_file(year)
        if any(keyword in re.sub('[^\w]', ' ', tweet).lower().split() for keyword in nomination_keywords)
    ]
    for award in awards:
        people_name_counts = Counter()
        ih = helpers.IMDBHandler()
        for tweet in nomination_tweets:
            people_names = [
                name.lower()
                for name in ih.get_names([tweet], False)
                if name.lower() not in stopwords
            ]
            people_name_counts.update(people_names)
        award_to_nominee_mapping[award] = [person_name for person_name, _ in people_name_counts.most_common(5)]

    return nominees

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
    # Your code here
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
    global yearly_tweets
    year = '2013' # todo
    yearly_tweets = get_tweets_from_file(year)
    get_hosts(year)
    get_awards(year)
    return

if __name__ == '__main__':
    main()
