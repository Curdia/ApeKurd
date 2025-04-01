import os
from atproto import Client
from langdetect import detect

# Load environment secrets
HANDLE = os.getenv("HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Debug output
print("DEBUG - HANDLE:", HANDLE or "❌ NOT SET")
print("DEBUG - APP_PASSWORD:", "✅ Loaded" if APP_PASSWORD else "❌ Missing")

# Check if secrets are present
if not HANDLE or not APP_PASSWORD:
    raise ValueError("❌ HANDLE or APP_PASSWORD not found. Check your GitHub Secrets.")

# 🎯 Supported hashtags
TARGET_HASHTAGS = ["#freekurdistan", "#kurd", "#kurdistan"]

# 🚫 Filtered words
BLACKLIST = ["hate", "racist", "nsfw", "spam", "violence"]

# 🔌 Connect to Bluesky
client = Client()
client.login(HANDLE, APP_PASSWORD)

# 🔍 Fetch posts with target hashtags
def get_tagged_posts():
    feed = client.app.bsky.feed.get_timeline()
    tagged = []
    for item in feed.feed:
        try:
            text = item.post.record.text
            if any(tag.lower() in text.lower() for tag in TARGET_HASHTAGS):
                tagged.append({
                    "uri": item.post.uri,
                    "cid": item.post.cid,
                    "text": text,
                    "author": item.post.author.handle
                })
        except Exception as e:
            print(f"Skipping item due to error: {e}")
            continue
    return tagged

# ✅ Check if the post is valid
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
    except Exception as e:
        print(f"Language detection failed: {e}")
        return False

# 📣 Share the best post
def share_top_post():
    posts = get_tagged_posts()
    print(f"Tagged posts found: {len(posts)}")
    if not posts:
        print("No posts found with the target hashtags.")
        return

    print("Listing tagged post texts:")
    for p in posts:
        print("—", p["text"])

    valid = [p for p in posts if is_valid_post(p["text"])]
    if not valid:
        print("⚠️ No valid tagged posts found.")
        return

    best = valid[0]
    used_tag = next((tag for tag in TARGET_HASHTAGS if tag.lower() in best['text'].lower()), TARGET_HASHTAGS[0])
    message = f"@{best['author']} used {used_tag} 👇\n\n{best['text']}"

    try:
        client.send_post(text=message)
        print("✅ Successfully shared the post.")
    except Exception as e:
        print(f"❌ Failed to share the post: {e}")

# ▶️ Run
if __name__ == "__main__":
    share_top_post()



