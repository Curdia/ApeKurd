import os
from atproto import Client
from langdetect import detect

# Load environment secrets
HANDLE = os.getenv("HANDLE")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# Debug output
print("DEBUG - HANDLE:", HANDLE or "❌ NOT SET")
print("DEBUG - APP_PASSWORD:", "✅ Loaded" if APP_PASSWORD else "❌ Missing")

if not HANDLE or not APP_PASSWORD:
    raise ValueError("❌ HANDLE or APP_PASSWORD not found. Check your GitHub Secrets.")

# 🎯 Target hashtags
TARGET_HASHTAGS = ["#freekurdistan", "#kurd", "#kurdistan"]
# 🚫 Words to avoid
BLACKLIST = ["hate", "racist", "nsfw", "spam", "violence"]

# 🔌 Connect to Bluesky
client = Client()
client.login(HANDLE, APP_PASSWORD)

# 📁 Check if a post was already shared
def has_been_shared(uri):
    if not os.path.exists("shared_posts.txt"):
        return False
    with open("shared_posts.txt", "r") as f:
        return uri in f.read()

# 📝 Mark post as shared
def mark_as_shared(uri):
    with open("shared_posts.txt", "a") as f:
        f.write(uri + "\n")

# 🔍 Fetch posts with hashtags
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
        print(f"Error while searching posts: {e}")
    return tagged

# ✅ Language + content filter
def is_valid_post(text):
    try:
        lang = detect(text)
        print(f"Detected language: {lang}")
        if lang not in ["en", "ku", "ckb", "kmr", "tr"]:
            return False
        if len(text.strip()) < 15:
            return False
        if any(word in text.lower() for word in BLACKLIST):
            return False
        return True
    except Exception as e:
        print(f"Language detection failed: {e}")
        return False

# 📣 Share most relevant unshared post
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

    # Find first unshared post
    best = None
    for post in valid:
        if not has_been_shared(post["uri"]):
            best = post
            break

    if not best:
        print("✅ All valid posts were already shared.")
        return

    # Build message
    used_tag = next((tag for tag in TARGET_HASHTAGS if tag.lower() in best['text'].lower()), TARGET_HASHTAGS[0])
    prefix = f"@{best['author']} used {used_tag} 👇\n\n"
    max_length = 300
    max_text_length = max_length - len(prefix)

    text_body = best['text']
    if len(prefix + text_body) > max_length:
        text_body = text_body[:max_text_length - 3] + "..."

    message = prefix + text_body

    try:
        client.send_post(text=message)
        mark_as_shared(best['uri'])  # ✅ Mark shared
        print("✅ Successfully shared the post.")
    except Exception as e:
        print(f"❌ Failed to share the post: {e}")

# ▶️ Run
if __name__ == "__main__":
    share_top_post()

