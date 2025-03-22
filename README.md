import os
import requests
from bs4 import BeautifulSoup
import tweepy

# === Ayarlar ===

TWEETED_FILE = "tweeted.txt"
KEYWORDS = ["son dakika", "breaking", "acil"]

# Twitter API bilgileri (GitHub Actions için secrets olarak ayarlanmalı)
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# === Yardımcı Fonksiyonlar ===

def is_recent(text):
    return any(kw in text.lower() for kw in KEYWORDS)

def load_tweeted():
    if not os.path.exists(TWEETED_FILE):
        return set()
    with open(TWEETED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_tweeted(tweeted_set):
    with open(TWEETED_FILE, "w", encoding="utf-8") as f:
        for link in tweeted_set:
            f.write(link + "\n")

# === Scraper Fonksiyonları ===

def scrape_rudaw():
    url = "https://www.rudaw.net/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]
        if is_recent(title) and link.startswith("http"):
            items.append({"title": title, "link": link})
    return items

def scrape_channel8():
    url = "https://channel8.com/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]
        if is_recent(title) and link.startswith("http"):
            items.append({"title": title, "link": link})
    return items

def scrape_ozgur_politika():
    url = "https://www.ozgurpolitika.com/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    items = []
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]
        if is_recent(title) and link.startswith("http"):
            items.append({"title": title, "link": link})
    return items

def get_all_latest_news():
    return scrape_rudaw() + scrape_channel8() + scrape_ozgur_politika()

# === Twitter Bot ===

def post_to_twitter(news_items, tweeted_links):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    for news in news_items:
        if news['link'] not in tweeted_links:
            tweet = f"Son Dakika: {news['title']}\n{news['link']}"
            try:
                api.update_status(tweet)
                print(f"Tweet atıldı: {tweet}")
                tweeted_links.add(news['link'])
                save_tweeted(tweeted_links)
            except Exception as e:
                print(f"Hata oluştu: {e}")

# === Ana Program ===

def main():
    print("Bot çalışıyor...")
    tweeted_links = load_tweeted()
    news_items = get_all_latest_news()
    post_to_twitter(news_items, tweeted_links)

if __name__ == "__main__":
    main()
