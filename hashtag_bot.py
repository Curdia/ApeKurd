import os
from atproto import Client
from langdetect import detect

# 🔐 Load secrets from environment
HANDLE = os.getenv("HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# 🛠 Debug info
print("DEBUG - HANDLE:", HANDLE or "❌ NOT SET")
print("DEBUG - APP_PASSWORD:", "✅ Loaded" if APP_PASSWORD else "❌ Missing")

if not HANDLE or not APP_PASSWORD:
    raise ValueError("❌ Missing HANDLE or APP_PASSWORD. Check your GitHub Secrets.")

# 🎯 Hashtags to track
TARGET_HASHTAGS = ["#freekurdistan", "#kurd", "#kurdistan"]

# 🚫 Content blacklist
BLACKLIST = ["hate", "racist", "nsfw", "spam", "violence"]

# 🔌 Connect to Bluesky
client = Client()
client.login(HANDLE, APP_PASSWORD)

# 📁 Check if URI was already shared
def has_been_shared(uri):
    if not os.path.exists("shared_posts.txt"):
        return False
    with open("shared_posts.txt", "r", encoding="utf-8") as f:
        shared_uris = {line.strip() for line in f if line.strip()}
        return uri.strip() in shared_uris

# 📝 Save URI to local shared list
def mark_as_shared(uri):
    with open("shared_posts.txt", "a", encoding="utf-8") as f:
        f.write(uri.strip() + "\n")
    print(f"✅ Marked as shared: {uri.strip()}")

# 🔍 Get all posts containing target hashtags
def get_tagged_posts():
    tagged = []
    try:
        for tag in TARGET_HASHTAGS:
            results = client.app.bsky.feed.search_posts({'q': tag})
            for item in results.posts:
                text = item.record.text
                if tag.lower() in text.lower():
                    tagged.append({
                        "uri": item.uri,
                        "cid": item.cid,
                        "text": text,
                        "author": item.author.handle
                    })
    except Exception as e:
        print(f"❌ Error during hashtag search: {e}")
    return tagged

# ✅ Language + blacklist filter
def is_valid_post(text):
    try:
        lang = detect(text)
        print(f"🌐 Detected language: {lang}")
        if lang not in ["en", "ku", "ckb", "kmr", "tr"]:
            return False
        if len(text.strip()) < 15:
            return False
        if any(word in text.lower() for word in BLACKLIST):
            return False
        return True
    except Exception as e:
        print(f"❌ Language detection failed: {e}")
        return False

# 📣 Share the first unshared valid post
def share_top_post():
    posts = get_tagged_posts()
    print(f"🔍 Found {len(posts)} total posts with hashtags.")

    if not posts:
        print("ℹ️ No hashtagged posts found.")
        return

    print("📄 Checking content validity...")
    valid_posts = [p for p in posts if is_valid_post(p["text"])]
    
    if not valid_posts:
        print("⚠️ No valid posts to share.")
        return

    best = None
    for post in valid_posts:
        if not has_been_shared(post["uri"]):
            best = post
            break

    if not best:
        print("✅ All valid posts have already been shared.")
        return

    # Prepare message
    used_tag = next((tag for tag in TARGET_HASHTAGS if tag.lower() in best["text"].lower()), TARGET_HASHTAGS[0])
    prefix = f"@{best['author']} used {used_tag} 👇\n\n"
    max_length = 300
    max_text_length = max_length - len(prefix)

    text_body = best["text"]
    if len(prefix + text_body) > max_length:
        text_body = text_body[:max_text_length - 3] + "..."

    message = prefix + text_body

    try:
        client.send_post(text=message)
        mark_as_shared(best["uri"])
        print("📢 Successfully shared.")
    except Exception as e:
        print(f"❌ Failed to share post: {e}")

# ▶️ Entry point
if __name__ == "__main__":
    share_top_post()

