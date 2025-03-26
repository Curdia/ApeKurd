import os
import zipfile

# Yeniden oluşturma işlemi
project_name = "apekurd-bluesky-hashtag-bot"
file_name = "hashtag_bot.py"
os.makedirs(project_name, exist_ok=True)

hashtag_bot_code = '''from atproto import Client
from langdetect import detect

# Bluesky credentials
HANDLE = "apekurd.bsky.social"
APP_PASSWORD = "qrzy-t7oz-m24a-psni"
TARGET_HASHTAG = "#freekurdistan"

# Kara liste
BLACKLIST = ["hate", "racist", "nsfw", "spam", "violence"]

# Initialize client
client = Client()
client.login(HANDLE, APP_PASSWORD)

# Timeline'dan hashtag içeren gönderileri çek
def get_tagged_posts():
    feed = client.app.bsky.feed.get_timeline()
    tagged = []
    for item in feed.feed:
        try:
            text = item.post.record.text
            if TARGET_HASHTAG.lower() in text.lower():
                tagged.append({
                    "uri": item.post.uri,
                    "cid": item.post.cid,
                    "text": text,
                    "author": item.post.author.handle
                })
        except Exception:
            continue
    return tagged

# İçerik filtresi
def is_valid_post(text):
    try:
        lang = detect(text)
        print(f"Detected language: {lang}")
        if lang not in ["en", "ku"]:
            return False
        if len(text.strip()) < 15:
            return False
        if any(word in text.lower() for word in BLACKLIST):
            return False
        return True
    except:
        return False

# Paylaşım yap
def share_top_post():
    posts = get_tagged_posts()
    print(f"Tagged posts found: {len(posts)}")
    print("Raw tagged texts:")
    for p in posts:
        print("—", p["text"])

    valid = [p for p in posts if is_valid_post(p["text"])]
    if not valid:
        print("⚠️ No valid tagged posts found.")
        return

    best = valid[0]
    message = f"@{best['author']} used {TARGET_HASHTAG} 👇\\n\\n{best['text']}"
    try:
        client.send_post(text=message)
        print("✅ Shared:", message)
    except Exception as e:
        print("❌ Error sharing post:", e)

if __name__ == "__main__":
    share_top_post()
'''

file_path = os.path.join(project_name, file_name)
with open(file_path, "w") as f:
    f.write(hashtag_bot_code)

# Zip oluştur
zip_path = f"/mnt/data/{project_name}.zip"
with zipfile.ZipFile(zip_path, "w") as zipf:
    zipf.write(file_path, arcname=file_name)

zip_path
