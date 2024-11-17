import tweepy
import pandas as pd
import json
from datetime import datetime
import s3fs
from config import bearer_token
import time

def run_twitter_etl():

    # Twitter API v2 credentials
    client = tweepy.Client(bearer_token=bearer_token)

    # Function to fetch tweets with retry mechanism
    def fetch_tweets(client, user_id, max_results, tweet_fields):
        while True:
            try:
                response = client.get_users_tweets(
                    id=user_id,
                    max_results=max_results,
                    tweet_fields=tweet_fields
                )
                return response.data
            except tweepy.errors.TooManyRequests:
                print("Rate limit exceeded. Waiting for 15 minutes...")
                time.sleep(15 * 60)  # Wait for 15 minutes

    # Fetch tweets with essential fields
    tweets = fetch_tweets(
        client=client,
        user_id='44196397',
        max_results=10,
        tweet_fields=['created_at', 'text', 'author_id', 'public_metrics']
    )

    # Process and save tweets to CSV
    tweet_list = []
    for tweet in tweets:
        refined_tweet = {
            "author_id": tweet.author_id,
            "text": tweet.text,
            "created_at": tweet.created_at,
            "public_metrics": tweet.public_metrics,
        }
        tweet_list.append(refined_tweet)

    df = pd.DataFrame(tweet_list)
    df.to_csv('s3://surya-twitter-bucket/refined_tweets.csv')