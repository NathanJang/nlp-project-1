import pandas as pd
import numpy as np
import spacy
import json
import gzip
import requests

class TweetReader:

  def sanitize_tweet(self, tweet):
    # remove mentions and hashtags from tweets
    pass

  def get_hosts_from_tweets(self, tweets):
    host_keyword = "host"
    host_negative_keyword = "next year"
    for tweet in tweets:
      tweet_text = tweet.get('text')
      if host_keyword in tweet_text and host_negative_keyword not in tweet_text:
        print(tweet)


class IDMB:
  def __init__(self):
    self.idmb_data_url = 'https://datasets.imdbws.com/name.basics.tsv.gz' # move to local?
    self.dataset_file_name = 'idmb_dataset.tsv.gz'
    self.names = {}

  def get_idmb_data(self):
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

def test_idmb():
  cls = IDMB()
  data_file_content = str(gzip.open(cls.dataset_file_name).read())
  data_file_content = data_file_content.split('\\n')
  split_file_content = [row.split('\\t') for row in data_file_content]
  column_names = split_file_content[0]
  idmb_df = pd.DataFrame(split_file_content, columns=column_names)
  idmb_df.drop(column_names[4:], axis=1, inplace=True)
  print(idmb_df.head)


# test_idmb()