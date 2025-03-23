import tweepy
import os
from langdetect import detect

# --- Load secrets from environment variables (GitHub Actions) ---
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

BOT_USERNAME = "@ApeKurd"

# --- Tweepy Auth ---
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# --- Content Filters ---
BLACKLIST = ["hate", "racist", "nsfw", "spam", "violence"]

def is_valid_tweet(text):
    try:
        lang = detect(text)
        if lang not in ["en", "ku"]:
            return False
        if len(text.strip()) < 15:
            return False
        if any(word in text.lower() for word in BLACKLIST):
            return False
        return True
    except:
        return False

def get_top_mention():
    mentions = api.mentions_timeline(count=20, tweet_mode="extended")
    valid_mentions = []
    for tweet in mentions:
        if is_valid_tweet(tweet.full_text):
            valid_mentions.append({
                "id": tweet.id,
                "user": tweet.user.screen_name,
                "likes": tweet.favorite_count
            })
    if not valid_mentions:
        return None
    return sorted(valid_mentions, key=lambda t: t["likes"], reverse=True)[0]

def share_top_tweet(tweet):
    tweet_url = f"https://twitter.com/{tweet['user']}/status/{tweet['id']}"
    status = f"@{tweet['user']} wrote 👇\n\n{tweet_url}"
    api.update_status(status=status)
    print("✅ Shared:", status)

# --- Run Bot ---
if __name__ == "__main__":
    top_tweet = get_top_mention()
    if top_tweet:
        share_top_tweet(top_tweet)
    else:
        print("No valid tweet to share.")
