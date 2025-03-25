from atproto import Client
from langdetect import detect

# 🔐 Bluesky credentials
HANDLE = "apekurd.bsky.social"
APP_PASSWORD = "qrzy-t7oz-m24a-psni"

# ❌ Kara liste kelimeler
BLACKLIST = ["hate", "racist", "nsfw", "spam", "violence"]

# 🔌 Bluesky API bağlantısı
client = Client()
client.login(HANDLE, APP_PASSWORD)

# 🔎 Mention içeren postları timeline üzerinden çek
def get_mentions():
    feed = client.app.bsky.feed.get_timeline()
    mentions = []
    for item in feed.feed:
        try:
            text = item.post.record.text
            if f"@{HANDLE}" in text:
                mentions.append({
                    "uri": item.post.uri,
                    "cid": item.post.cid,
                    "text": text,
                    "author": item.post.author.handle
                })
        except AttributeError:
            continue  # bazı postlar (repost, image-only) text içermeyebilir
    return mentions

# ✅ İçerik filtresi
def is_valid_post(text):
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

# 📣 Geçerli postu paylaş
def share_top_post():
    mentions = get_mentions()
    print(f"Mentions found: {len(mentions)}")
    print("Raw mention texts:")
    for m in mentions:
        print("—", m["text"])
    
    valid = [m for m in mentions if is_valid_post(m["text"])]
    if not valid:
        print("⚠️ No valid mentions found.")
        return

    best = valid[0]
    message = f"@{best['author']} wrote 👇\n\n{best['text']}"
    try:
        client.send_post(text=message)
        print("✅ Shared:", message)
    except Exception as e:
        print("❌ Error sharing post:", e)

# ▶️ Çalıştır
if __name__ == "__main__":
    share_top_post()
