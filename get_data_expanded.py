from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os
import time

# Đọc API Key từ file .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_youtube_data_expanded(queries, max_pages=3):
    all_data = []
    for q in queries:
        print(f"\n🔍 Đang lấy dữ liệu cho: '{q}'...")
        next_page_token = None
        page_count = 0
        
        while page_count < max_pages:
            try:
                # 1. Tìm kiếm video (có pagination)
                search_params = {
                    'q': q,
                    'part': 'snippet',
                    'maxResults': 50,
                    'type': 'video',
                    'order': 'relevance',
                }
                if next_page_token:
                    search_params['pageToken'] = next_page_token
                
                search_response = youtube.search().list(**search_params).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
                
                if not video_ids:
                    print(f"   ⚠ Không tìm thấy thêm video.")
                    break
                
                # 2. Lấy chi tiết thống kê
                video_response = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids)
                ).execute()
                
                for item in video_response.get('items', []):
                    all_data.append({
                        'Query': q,
                        'Video_ID': item['id'],
                        'Published_At': item['snippet']['publishedAt'],
                        'Channel_Title': item['snippet']['channelTitle'],
                        'Title': item['snippet']['title'],
                        'Description': item['snippet']['description'],
                        'Tags': ",".join(item['snippet'].get('tags', [])),
                        'Category_ID': item['snippet'].get('categoryId', ''),
                        'View_Count': int(item['statistics'].get('viewCount', 0)),
                        'Like_Count': int(item['statistics'].get('likeCount', 0)),
                        'Comment_Count': int(item['statistics'].get('commentCount', 0)),
                        'Favorite_Count': int(item['statistics'].get('favoriteCount', 0)),
                    })
                
                page_count += 1
                next_page_token = search_response.get('nextPageToken')
                
                print(f"   ✅ Trang {page_count}: lấy được {len(video_response.get('items', []))} video (tổng: {len(all_data)})")
                
                if not next_page_token:
                    break
                
                # Nghỉ 1 giây để tránh bị rate limit
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Lỗi: {e}")
                # Nếu bị quota limit thì dừng
                if "quotaExceeded" in str(e) or "rateLimitExceeded" in str(e):
                    print("\n⚠️  ĐÃ HẾT QUOTA API! Lưu dữ liệu đã lấy được...")
                    break
                time.sleep(2)
                break
        
        # Nghỉ giữa mỗi keyword
        time.sleep(0.5)
    
    return pd.DataFrame(all_data)



keywords = [
    # --- Xu hướng chung ---
    "flower arrangement trends 2024",
    "flower arrangement trends 2025",
    "wedding flower trends 2025",
    "popular flowers for gift",
    "florist business trends",
    "floral design ideas 2025",
    
    # --- Từng loại hoa cụ thể ---
    "rose bouquet trending",
    "tulip arrangement ideas",
    "orchid decoration trends",
    "sunflower bouquet popular",
    "peony wedding flowers",
    "hydrangea arrangement trending",
    "lily flower gift ideas",
    "dahlia floral design",
    "lavender bouquet trending",
    "chrysanthemum decoration ideas",
    "ranunculus wedding bouquet",
    "carnation flower arrangement",
    
    # --- Theo sự kiện ---
    "valentine flowers trending",
    "wedding bouquet ideas 2025",
    "birthday flower gift ideas",
    "funeral flowers arrangement",
    "christmas flower decoration",
    "mother's day flower trends",
    "graduation flower bouquet",
    
    # --- Theo phong cách ---
    "minimalist flower arrangement",
    "luxury floral design",
    "dried flower arrangement trending",
    "sustainable floristry trends",
    "boho wedding flowers",
    
    # --- Business & Market ---
    "flower shop business tips",
    "floral industry trends 2025",
    "best selling flowers 2024",
    "flower market demand",
]

if __name__ == "__main__":
    print("=" * 60)
    print("  YOUTUBE DATA COLLECTION - EXPANDED VERSION")
    print(f"  Số keywords: {len(keywords)}")
    print(f"  Max pages/keyword: 2 (tối đa ~100 video/keyword)")
    print(f"  Ước tính: {len(keywords) * 100} video tối đa")
    print("=" * 60)
    
    # Lấy 2 trang mỗi keyword (khoảng 100 video/keyword)
    # Nếu muốn ít hơn để tiết kiệm quota, đặt max_pages=1
    df = get_youtube_data_expanded(keywords, max_pages=2)
    
    # Loại bỏ video trùng lặp (cùng Video_ID)
    before = len(df)
    df = df.drop_duplicates(subset='Video_ID', keep='first')
    after = len(df)
    print(f"\n📊 Loại bỏ {before - after} video trùng lặp")
    
    # Lưu file
    df.to_csv("flower_social_data_expanded.csv", index=False, encoding='utf-8-sig')
    
    print(f"\n{'=' * 60}")
    print(f"  ✅ HOÀN THÀNH!")
    print(f"  📁 Đã lưu {len(df)} dòng dữ liệu")
    print(f"  📁 File: flower_social_data_expanded.csv")
    print(f"  📁 Keywords đã quét: {df['Query'].nunique()}")
    print(f"{'=' * 60}")
    
    # Thống kê nhanh
    print(f"\n📈 Thống kê:")
    print(f"  - Tổng video: {len(df)}")
    print(f"  - Tổng views: {df['View_Count'].sum():,.0f}")
    print(f"  - Trung bình views: {df['View_Count'].mean():,.0f}")
    print(f"  - Video nhiều views nhất: {df['View_Count'].max():,.0f}")
    print(f"\n  Số video theo keyword:")
    print(df['Query'].value_counts().to_string())
