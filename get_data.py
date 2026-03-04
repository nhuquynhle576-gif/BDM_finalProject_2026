from googleapiclient.discovery import build
import pandas as pd
from dotenv import load_dotenv
import os

# Đọc API Key từ file .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_youtube_data(queries):
    all_data = []
    for q in queries:
        print(f"Đang lấy dữ liệu cho từ khóa: {q}...")
        # 1. Tìm kiếm video
        search_request = youtube.search().list(
            q=q,
            part='snippet',
            maxResults=50,
            type='video'
        ).execute()

        video_ids = [item['id']['videoId'] for item in search_request['items']]
        
        # 2. Lấy chi tiết thống kê
        video_request = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()

        for item in video_request['items']:
            all_data.append({
                'Query': q,
                'Published_At': item['snippet']['publishedAt'],
                'Channel_Title': item['snippet']['channelTitle'],
                'Title': item['snippet']['title'],
                'Description': item['snippet']['description'],
                'Tags': ",".join(item['snippet'].get('tags', [])),
                'View_Count': int(item['statistics'].get('viewCount', 0)),
                'Like_Count': int(item['statistics'].get('likeCount', 0)),
                'Comment_Count': int(item['statistics'].get('commentCount', 0))
            })
    
    return pd.DataFrame(all_data)

# Danh sách từ khóa để quét đúng mục tiêu của thầy giáo
keywords = [
    "flower arrangement trends 2024",
    "wedding flower trends 2025",
    "popular flowers for gift",
    "florist business trends",
    "floral design ideas 2025"
]

# Chạy và lưu file
df = get_youtube_data(keywords)
df.to_csv("flower_social_data.csv", index=False, encoding='utf-8-sig')
print(f"Hoàn thành! Đã lưu {len(df)} dòng dữ liệu vào file flower_social_data.csv")
