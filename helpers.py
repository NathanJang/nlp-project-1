import pandas as pd
import numpy as np
import spacy
import json
import gzip
import requests
import imdb
import re
from collections import Counter

# todo: move or use nlp library stoplist
stop_list = ['GoldenGlobes', 'Golden', 'Globes', 'Golden Globes', 'RT', 'VanityFair', 'golden', 'globes' '@', 'I', 'we', 'http', '://', '/', 'com', 'Best', 'best', 'Looking', 'Nice', 'Most', 'Pop', 'Hip Hop', 'Rap', 'We', 'Love', 'Awkward','Piece', 'While', 'Boo', 'Yay', 'Congrats', 'And', 'The', 'Gq', 'Refinery29', 'USWeekly', 'TMZ', 'Hollywood', 'Watching', 'Hooray', 'That', 'Yeah', 'Can', 'So', 'And', 'But', 'What', 'NShowBiz', 'She', 'Mejor', 'Did', 'Vanity', 'Fair', 'Drama', 'MotionPicture', 'News', 'Take', 'Before', 'Director', 'Award', 'Movie Award', 'Music Award', 'Best Director', 'Best Actor', 'Best Actress', 'Am', 'Golden Globe', 'Globe', 'Awards', 'It']


class TweetHandler:

  def sanitize_tweet(self, tweet):
    # remove mentions and hashtags from tweets
    pass

  def get_host_tweets(self, tweets):
    host_tweets = []
    host_keyword = "host"
    host_negative_keyword = "next year"

    # add all tweets mentioning the host keyword
    for tweet in tweets:
      if host_keyword in tweet and host_negative_keyword not in tweet:
        host_tweets.append(tweet)

    return host_tweets

  # todo: move?
  def get_most_common_names(self, names, variance=25):
    variance_factor = variance/100
    found_hosts = []
    # get most common names using a Counter
    count = Counter(names)
    common_hosts = count.most_common(len(count))
    top_mentioned_host = common_hosts[0][1]
    for host in common_hosts:
      if host[1] > (top_mentioned_host * variance_factor):
        found_hosts.append(host[0])
    return found_hosts


class IMDBHandler:
  def __init__(self):
    self.idmb_data_url = 'https://datasets.imdbws.com/name.basics.tsv.gz' # move to local?
    self.dataset_file_name = 'idmb_dataset.tsv.gz'
    self.names = {}
    self.imdb_client = imdb.IMDb()

  def get_names(self, tweets, use_imdb_database=True):
    '''Returns a list of names extracted from tweets by regex matching and imdb lookup

    :param tweets: list, tweets text
    :param use_imdb_database: default = true, looks up the person in the imdb database (slower)
    :return: list of potential names
    '''
    names = []
    people = []
    regex_name_matching = '([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)'
    # regex to get names from tweets
    for tweet in tweets:
      people += re.findall(regex_name_matching, ''.join(tweet))

    for person in people:
      if person not in stop_list:
        if use_imdb_database and not (person in names or self.imdb_client.search_person(person)):
          continue
        names.append(person)

    return names

  def get_imdb_data(self):
    '''Gets imdb dataset from their website and converts it into a pandas datframe.

    :return: pandas dataframe containing names and birth/death days of people
    '''
    data_response = requests.get(self.idmb_data_url,
                                 allow_redirects=True,
                                 stream=True)
    if data_response.status_code == 200:
      print('successfully retrieved idmb data set file')
      with open(self.dataset_file_name, 'wb') as data_file:
        # read, clean and split dataset file
        data_file.write(data_response.raw.read())
        data_file_content = str(gzip.open(self.dataset_file_name).read())
        data_file_content = data_file_content.split('\\n')
        split_file_content = [row.split('\\t') for row in data_file_content]
        # create pandas dataframe for idbm data
        column_names = split_file_content[0]
        idmb_df = pd.DataFrame(split_file_content[1:-1], columns=column_names)
        # drop unnecessary columns
        idmb_df.drop(column_names[4:], axis=1, inplace=True)
        print(idmb_df.head)
        return idmb_df
    else:
      print('Unable to retrieve data set file.')
      raise Exception(f'IDMB file could not be downloaded. Status code: {data_response.status_code}')

# def test_idmb():
#   cls = IMDBHandler()
#   data_file_content = str(gzip.open(cls.dataset_file_name).read())
#   data_file_content = data_file_content.split('\\n')
#   split_file_content = [row.split('\\t') for row in data_file_content]
#   column_names = split_file_content[0]
#   idmb_df = pd.DataFrame(split_file_content, columns=column_names)
#   idmb_df.drop(column_names[4:], axis=1, inplace=True)
#   print(idmb_df.head)

# test_idmb()