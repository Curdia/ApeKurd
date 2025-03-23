import tweepy
import os
import time
from langdetect import detect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_KEY = os.getenv("be9oCEz16rBI9p7UCb4zPUAse")
API_SECRET = os.getenv("YGoRaH7nxzXSWVwZoqohi7xjNPOqMOXdvLDTpIVy0nTxymRaUR")
ACCESS_TOKEN = os.getenv("1903848150709805056-o9DakpwrUB5R1BvvJOgUHBIlM1yqI0")
ACCESS_SECRET = os.getenv("YBSjJbCXAoipsL4ZaFvC6RzwIQAp0EjwgnFdgLiIdqB6X")
BOT_USERNAME = "@APEKURD"

# --- Blacklist / Filters ---
BLACKLIST_WORDS = ["hate", "racist", "spam", "nsfw", "violence"]

def is_valid_tweet(text):
    try:
        language = detect(text)
        if language not in ["en", "ku"]:  # English or Kurdish only
            return False
        if len(text.strip()) < 15:
            return False
        if any(bad_word in text.lower() for bad_word in BLACKLIST_WORDS):
            return False
        return True
    except:
        return False

# --- Twitter Auth ---
def create_api():
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)

# --- Get Mentions ---
def fetch_valid_mentions(api, count=20):
    mentions = api.mentions_timeline(count=count, tweet_mode="extended")
    valid = []
    for tweet in mentions:
        if is_valid_tweet(tweet.full_text):
            valid.append({
                "id": tweet.id,
                "user": tweet.user.screen_name,
                "likes": tweet.favorite_count,
                "text": tweet.full_text
            })
    return sorted(valid, key=lambda x: x["likes"], reverse=True)

# --- Quote Top Tweet ---
def quote_top_tweet(api, tweets):
    if not tweets:
        print("No valid tweets found.")
        return
    top = tweets[0]
    tweet_url = f"https://twitter.com/{top['user']}/status/{top['id']}"
    status = f"@{top['user']} wrote 👇\n\n{tweet_url}"
    api.update_status(status=status)
    print("Tweet shared successfully:", status)

# --- Main Execution ---
if __name__ == "__main__":
    api = create_api()
    mentions = fetch_valid_mentions(api)
    quote_top_tweet(api, mentions)
