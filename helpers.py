from difflib import SequenceMatcher

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

  def get_awards_tweets(self, tweets):
    # todo: function description and check return type
    awards_matching_string = 'Best ([A-z\s-]+)[A-Z][a-z]*[^A-z]'
    other_matching_string = '.*^((?!(goes|but|is)).)*$'
    regex_matching_pattern = re.compile(awards_matching_string)
    awards_tweets = []
    cleaned_tweets = []
    for tweet in tweets:
      if regex_matching_pattern.match(tweet):
        awards_tweets.append(regex_matching_pattern.search(tweet).group(0)[:-1])
    regex_matching_pattern = re.compile(other_matching_string)
    for tweet in awards_tweets:
      if regex_matching_pattern.match(tweet):
        cleaned_tweets.append(regex_matching_pattern.match(tweet).group(0).lower())

    return cleaned_tweets

  def get_nominee_tweets(self, tweets):
    # nominees_matching_string = '[A-z\s]+'
    return tweets
    '''
    nomination_match = 'nomin(at(e[sd]?|ing|ion)|ees?)'
    other_matching_string = '.*^((?!(goes|but|is)).)*$'
    pattern_before = re.compile(nomination_match, re.IGNORECASE)
    # pattern_after = re.compile(nominees_matching_string + '\s+' + nomination_match, re.IGNORECASE)
    nominee_tweets = []
    # cleaned_tweets = []
    for tweet in tweets:
      results_searching_before = pattern_before.search(tweet)
      # results_searching_after = pattern_after.search(tweet)
      if results_searching_before:
        # nominee_tweets.append(results_searching_before.group(0))
        nominee_tweets.append(tweet)
      # elif results_searching_after:
        # nominee_tweets.append(results_searching_after.group(0))
        # nominee_tweets.append(tweet)
    # regex_matching_pattern = re.compile(other_matching_string)
    # for tweet in awards_tweets:
    #   if regex_matching_pattern.match(tweet):
    #     cleaned_tweets.append(regex_matching_pattern.match(tweet).group(0).lower())

    return nominee_tweets
    # relevant_tweets = []
    # for tweet in tweets:
    #   adder = False
    #   for match in award_mapping[award]:
    #     if match.lower() in tweet.lower() or match.lower()[0:int(len(match.lower()) / 2)] in tweet.lower():
    #       adder = True
    #   if adder:
    #     relevant_tweets.append(tweet)
    # return relevant_tweets
    '''

  def process_awards_tweets(self, tweets, cleaned_tweets, nlp_client, official_awards):
    awards_len = len(official_awards)
    matching_intersection_threshold = 3
    awards_tokens = {}
    award_mapping = {}

    # initialize a mapping for awards and their respective tokens for titles
    for award in official_awards:
        for token in nlp_client(award):
            if award not in awards_tokens:
                awards_tokens[award] = [str(token)]
                award_mapping[award] = [award]
            else:
              awards_tokens[award].append(str(token))
              award_mapping[award] = []
    # create a matrix to identify the official awards so we cna compare to awards found in our tweets
    matrix = [[0 for j in range(awards_len)] for i in range(len(cleaned_tweets))]
    for i in range(len(cleaned_tweets)):
        # get tokens for the cleaned tweets that have an award in them
        nlp_tokens = set([str(token) for token in nlp_client(cleaned_tweets[i])])
        for j in range(awards_len):
            # mark the intersection between the tokens of official awards and our tweets
            matrix[i][j] = len(nlp_tokens.intersection(set(awards_tokens[official_awards[j]])))

    for i in range(len(matrix)):
        # append the highest scored intersections in our matching matrix between official awards and out found awards
        max_index = matrix[i].index(max(matrix[i]))
        if matrix[i][max_index] > matching_intersection_threshold:
            award_mapping[official_awards[max_index]].append(cleaned_tweets[i])

    return award_mapping

  def get_most_common_names(self, names, variance=25):
    variance_factor = variance/100
    found_hosts = []
    # get most common names using a Counter
    count = Counter(names)
    common_hosts = count.most_common(len(count))
    if not common_hosts:
      return found_hosts

    top_mentioned_host = common_hosts[0][1]
    for host in common_hosts:
      if host[1] > (top_mentioned_host * variance_factor):
        found_hosts.append(host[0])

    # todo: better way to do this
    # hacky but removes any non-names by seeing if their split length is 1
    return [host for host in found_hosts if len(host.split(' ')) > 1]

  word_similarity_factor = lambda self, lhs, rhs: SequenceMatcher(None, lhs, rhs).ratio()

  def fuzzy_list_includes(self, a_list, v):
    '''If v is in a_list (with some fuzziness margin), return the existing value in the list, or None if none.'''
    return next(
      (
        existing
        for existing in a_list
        if self.word_similarity_factor(existing.lower(), v.lower()) >= 0.66
        or existing.lower() in v.lower()
        or v.lower() in existing.lower()
      ),
      None
    )


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

    self.names = names
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


class ResultsHandler:
  def __init__(self, official_awards):
    self.official_awards = official_awards

  def print_results(self, hosts=[], nominees={}, winners={}, presenters={}):
    results = ""
    # display hosts
    results += "Hosts: " if len(hosts) > 1 else "Host: "
    for host in hosts:
      results += f'{host}, '
    results = results[:-2] + "\n\n"

    # Awards
    for i in range(len(self.official_awards)):
      award = self.official_awards[i]
      results += f'Award: {award}\n'
      results += "Presenters: "
      for presenter in presenters[award]:
        results += f'{presenter}, '
      results = results[:-2] + "\n"

      results += "Nominees: "
      for nominee in nominees[award]:
        results += f'{nominee}, '
      results = results[:-2] + "\n"

      results += f'Winner: {winners[award]}\n\n'

    return results

  def json_results(self, hosts=[], nominees={}, winners={}, presenters={}):
    json_output = {'hosts': hosts, 'award_data': {}}
    for award in self.official_awards:
      json_output['award_data'][award] = {
        'presenters': presenters[award],
        'nominees': nominees[award],
        'winner': winners[award]
      }
    return json_output


class TweetTokenizer:
  def __init__(self, nlp_client, nlp_tokenizer):
    self.patterns = {'name': '[A-Z][a-z]*\s[\w]+'}
    self.keywords = {'ceremony': ["#", "goldenglobes", "golden", "globes", "#goldenglobes"],
                     'category': {"PERSON": ["actor", "actress", "director", "cecil"]}}
    self.stopwords = ['this year', 'tonight']
    self.nlp = nlp_client
    self.nlp_tokenizer = nlp_tokenizer
    self.award_tokens = set()

  def add_tokens_from_awards(self, official_awards):
    for official_award in official_awards:
      for tok in self.nlp_tokenizer(official_award):
        self.award_tokens.add(str(tok))

  def add_tokens_from_keywords(self):
    for keyword in self.keywords:
      self.award_tokens.add(keyword)

  def get_relevant_words(self, tweets, type):
    words = {}
    name_pattern = re.compile(self.patterns['name'])
    for tweet in tweets:
      # if yearly_tweets[tweet] is None:
      #   yearly_tweets[tweet] = self.nlp(tweet).ents
      for ent in self.nlp(tweet).ents:
        if ent.label_ in ['ORDINAL', 'CARDINAL', 'QUANTITY', 'MONEY', 'DATE', 'TIME']:
          continue
        cleaned_entity = ent.text.strip()
        if cleaned_entity.lower() in self.stopwords:
          continue
        if type == 'PERSON' and name_pattern.match(cleaned_entity) is None:
          continue
        if (type == 'PERSON' and ent.label_ == 'PERSON') or type == 'WORK_OF_ART':
          ents = self.nlp_tokenizer(cleaned_entity)
          tokens = set()
          for token in ents:
            tokens.add(str(token).lower())
          intersect = tokens.intersection(self.award_tokens)
          if len(intersect) < int(len(tokens) / 2) or len(intersect) == 0:
            if cleaned_entity in words:
              words[cleaned_entity] += 1
            else:
              words[cleaned_entity] = 1
    return words

  def get_presenters(self, tweets, award, winners):
    words = {}
    for tweet in tweets:
      for ent in self.nlp(tweet).ents:
        cleaned_entity = ent.text.strip()
        if str(cleaned_entity).lower().startswith("rt"):
          continue
        if str(cleaned_entity).lower() in winners[award][0].lower():
          continue
        ents = self.nlp_tokenizer(cleaned_entity)
        tokens = set()
        for token in ents:
          tokens.add(str(token).lower())
        intersect = tokens.intersection(self.award_tokens)
        if len(intersect) < int(len(tokens) / 2) or len(intersect) == 0:
          if cleaned_entity in words:
            words[cleaned_entity] += 1
          else:
            words[cleaned_entity] = 1
    return words

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