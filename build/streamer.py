import tweepy
import calendar
import json
import re
import nltk
from textblob import TextBlob
import tables
import sqlite3

class MyStreamListener(tweepy.StreamListener):

    def __init__(self, cnx, cur, app):
        self.cnx = cnx
        self.cur = cur
        self.index = 1
        self.app = app

    def on_data(self, data):
        month_name = dict((v,k) for k,v in enumerate(calendar.month_abbr))
        my_data = json.loads(data)
        #if streaming too much data, nothing gets returned.
        if 'limit' in my_data: 
            pass
        else:
            country = None
            #tweet information ------------------------------------------------------
            if my_data['place']:
                country = my_data['place']['country']
            user_name = my_data['user']['screen_name']
            verified = str(my_data['user']['verified'])
            t_ca = my_data['created_at']
            nt_ca = t_ca[-1:-5:-1][::-1] + '-' + str(month_name[t_ca[4:7]]) + '-'\
                    + t_ca[8:11] + t_ca[11:19]
            if 'media' in my_data['entities']:
                media_type = my_data['entities']['media'][0]['type']
            else: media_type = None
            if 'retweeted_status' in my_data:
                top = re.search('RT @\w*:', my_data['text'])
                if my_data['retweeted_status']["truncated"]:
                    subt = my_data['retweeted_status']['extended_tweet']['full_text']
                else:
                    subt = my_data['retweeted_status']['text']
                tweet = top.group() + " " + subt
            else:
                if my_data["truncated"]:
                    tweet = str(my_data['extended_tweet']['full_text'])
                    tweet_es = str(my_data['extended_tweet']['full_text'])
                else: 
                    tweet = str(my_data['text'])
                    tweet_es = str(my_data['text'])
            tweet = re.sub('[\'\"]+|\\\'|\\\"', '`', tweet)
            tweet = tweet.replace("\\", "|")
            clean_tweet = ' '.join(re.sub("https://\w+\.co/\w+|RT|@|#|\W|[0-9]+", " ",
                                          tweet).split())
            tb_ct = TextBlob(clean_tweet)
            if tb_ct.sentiment.polarity > 0:
                sentiment = 'Positive'
            elif tb_ct.sentiment.polarity == 0:
                sentiment = 'Neutral'
            else: 
                sentiment = 'Negative'
            tweet_input = f"""INSERT INTO tweets VALUES({verified},'{nt_ca}',
                          '{tweet}', '{sentiment}', '{media_type}',
                          '{user_name}', '{country}')"""
            if country is None:
                country = 'None'
            if media_type is None:
                media_type = 'None'
            #insert into SQL!!!!!!!------------------------------------------
            cnx = sqlite3.connect('tweets.db')
            cur = cnx.cursor()
            cur.execute(tweet_input)
            cnx.commit()
            cur.close()
            cnx.close()
            if len(self.app.tweet_list.get_children()) < 50:
                if self.index % 10 == 0:
                    y_place = self.app.tweet_list.yview()[0]
                    x_place = self.app.tweet_list.xview()[0]
                    self.app.populate_list()
                    self.app.tweet_list.yview_moveto(y_place)
                    self.app.tweet_list.xview_moveto(x_place)                    
                self.index +=1
            else:
                self.app.live_update()
                self.index = 1

    def on_error(self, status_code):
        if status_code != 200:
            return False
    
    def on_connect(self):
        print('Connected to the twitter API.')  
