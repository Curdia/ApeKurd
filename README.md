import os
import requests
from bs4 import BeautifulSoup
import tweepy

TWEETED_FILE = "tweeted.txt"
KEYWORDS = ["son dakika", "breaking", "acil"]

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

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

def scrape_site(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    headlines = []
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]
        if is_recent(title) and link.startswith("http"):
            headlines.append({"title": title, "link": link})
    return headlines

def get_all_news():
    sites = [
        "https://www.rudaw.net/",
        "https://channel8.com/",
        "https://www.ozgurpolitika.com/"
    ]
    all_news = []
    for site in sites:
        try:
            all_news += scrape_site(site)
        except Exception as e:
            print(f"{site} okunamadı: {e}")
    return all_news

def post_to_twitter(news_list, tweeted_links):
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    for news in news_list:
        if news["link"] not in tweeted_links:
            tweet = f"Son Dakika: {news['title']}\n{news['link']}"
            try:
                api.update_status(tweet)
                print(f"Tweet atıldı: {tweet}")
                tweeted_links.add(news["link"])
                save_tweeted(tweeted_links)
            except Exception as e:
                print(f"Tweet atılamadı: {e}")

def main():
    print("Bot başlıyor...")
    tweeted = load_tweeted()
    news = get_all_news()
    post_to_twitter(news, tweeted)

if __name__ == "__main__":
    main()
