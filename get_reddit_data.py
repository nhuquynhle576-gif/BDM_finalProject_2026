"""
=============================================================================
  REDDIT DATA COLLECTION
  Lấy dữ liệu từ Reddit về xu hướng hoa
  
  THƯ VIỆN CẦN CÀI: pip install praw pandas python-dotenv
  
  HƯỚNG DẪN:
  1. Vào https://www.reddit.com/prefs/apps
  2. Nhấn "create another app..." → chọn "script"
  3. Điền redirect uri: http://localhost:8080
  4. Copy client_id và client_secret rồi dán vào file .env
=============================================================================
"""
import praw
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
import time

# Đọc API Keys từ file .env
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")

# Kết nối Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent="flower_research_bot/1.0 by " + str(REDDIT_USERNAME)
)

# Kiểm tra kết nối
print(f"✅ Đã kết nối Reddit thành công! User: {reddit.user.me()}")

# =============================================================================
# CÁC SUBREDDIT LIÊN QUAN ĐẾN HOA
# =============================================================================
subreddits = [
    "flowers",
    "flowerarranging",
    "florists",
    "weddingplanning",
    "gardening",
    "bouquets",
    "IndoorGarden",
    "orchids",
    "roses",
    "succulents",
    "houseplants",
]

# Từ khóa tìm kiếm
search_queries = [
    "flower trends",
    "popular flowers",
    "wedding flowers 2025",
    "best flowers for gift",
    "flower arrangement ideas",
    "trending flowers",
    "flower business",
    "flower delivery trending",
    "seasonal flowers",
    "flower bouquet ideas",
    "rose arrangement",
    "tulip trending",
    "orchid popular",
    "sunflower decoration",
    "peony wedding",
    "hydrangea arrangement",
    "dried flowers trend",
    "sustainable floristry",
]

def collect_subreddit_posts(subreddit_name, limit=100):
    """Lấy bài viết từ 1 subreddit"""
    posts = []
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        for sort_type, method in [("hot", subreddit.hot),
                                   ("top", subreddit.top),
                                   ("new", subreddit.new)]:
            try:
                for post in method(limit=limit):
                    posts.append({
                        'Source': 'Reddit',
                        'Subreddit': subreddit_name,
                        'Sort_Type': sort_type,
                        'Post_ID': post.id,
                        'Title': post.title,
                        'Selftext': post.selftext[:1000] if post.selftext else '',
                        'Author': str(post.author) if post.author else '[deleted]',
                        'Score': post.score,
                        'Upvote_Ratio': post.upvote_ratio,
                        'Num_Comments': post.num_comments,
                        'Created_UTC': datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                        'URL': post.url,
                        'Is_Video': post.is_video,
                        'Link_Flair_Text': post.link_flair_text if post.link_flair_text else '',
                        'Over_18': post.over_18,
                    })
            except Exception as e:
                print(f"  ⚠  Lỗi lấy {sort_type} từ r/{subreddit_name}: {e}")

        print(f"  ✅ r/{subreddit_name}: {len(posts)} bài viết")

    except Exception as e:
        print(f"  ❌ Không thể truy cập r/{subreddit_name}: {e}")

    return posts


def search_reddit_posts(query, limit=100):
    """Tìm kiếm bài viết trên toàn Reddit"""
    posts = []
    try:
        for post in reddit.subreddit("all").search(query, sort="relevance", limit=limit):
            posts.append({
                'Source': 'Reddit',
                'Subreddit': str(post.subreddit),
                'Sort_Type': 'search',
                'Post_ID': post.id,
                'Title': post.title,
                'Selftext': post.selftext[:1000] if post.selftext else '',
                'Author': str(post.author) if post.author else '[deleted]',
                'Score': post.score,
                'Upvote_Ratio': post.upvote_ratio,
                'Num_Comments': post.num_comments,
                'Created_UTC': datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'URL': post.url,
                'Is_Video': post.is_video,
                'Link_Flair_Text': post.link_flair_text if post.link_flair_text else '',
                'Over_18': post.over_18,
            })

        print(f"  ✅ Search '{query}': {len(posts)} bài viết")

    except Exception as e:
        print(f"  ❌ Search '{query}' lỗi: {e}")

    return posts


# =============================================================================
# CHÍNH - THU THẬP DỮ LIỆU
# =============================================================================
if __name__ == "__main__":
    all_posts = []

    print("=" * 60)
    print("  REDDIT DATA COLLECTION")
    print("=" * 60)

    # 1. Lấy từ các subreddit
    print("\n📂 [PHASE 1] Lấy bài viết từ các subreddit...")
    for sub in subreddits:
        posts = collect_subreddit_posts(sub, limit=100)
        all_posts.extend(posts)
        time.sleep(1)

    # 2. Tìm kiếm theo keywords
    print("\n🔍 [PHASE 2] Tìm kiếm theo keywords...")
    for query in search_queries:
        posts = search_reddit_posts(query, limit=50)
        all_posts.extend(posts)
        time.sleep(1)

    # 3. Tạo DataFrame và loại trùng
    df = pd.DataFrame(all_posts)
    before = len(df)
    df = df.drop_duplicates(subset='Post_ID', keep='first')
    after = len(df)

    # 4. Lưu file
    df.to_csv("reddit_flower_data.csv", index=False, encoding='utf-8-sig')

    print(f"\n{'=' * 60}")
    print(f"  ✅ HOÀN THÀNH!")
    print(f"  📊 Tổng bài viết: {len(df)} (loại {before - after} trùng)")
    print(f"  📁 File: reddit_flower_data.csv")
    print(f"  📁 Subreddits: {df['Subreddit'].nunique()}")
    print(f"{'=' * 60}")
