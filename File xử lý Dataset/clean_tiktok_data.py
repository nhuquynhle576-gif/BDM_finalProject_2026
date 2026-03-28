import pandas as pd
import os
import re
import emoji
import unicodedata
import glob

def clean_caption_text(text):
    if pd.isna(text):
        return text
    text = str(text)
    
    # Chuẩn hóa font chữ kiểu (ví dụ 𝐓𝐈𝐄̣̂𝐌 𝐇𝐎𝐀 -> TIỆM HOA) để bộ lọc có thể nhận diện được
    text = unicodedata.normalize('NFKC', text)
    
    # 1. Cắt bỏ toàn bộ phần sau các đường kẻ phân cách dài (---, ===, ___, ...)
    text = re.split(r'[-=_]{4,}', text)[0]
    
    # 2. Quét từ khóa liên hệ và cắt bỏ toàn bộ từ vị trí đó đến cuối bài
    contact_keywords = r'(?i)(hotline|add\s*:|địa chỉ\s*:|zalo|z\.lo|sđt|điện thoại|ig\s*:|instagram|liên hệ|inbox|tiệm hoa|chi nhánh|cs\d:|cơ sở|website|shopee)'
    match = re.search(contact_keywords, text)
    if match:
        text = text[:match.start()] # Cắt lấy phần từ đầu đến ngay trước từ khóa
        
    # 3. Remove emojis
    text = emoji.replace_emoji(text, replace='')
    
    # 4. Remove tags (e.g. #hoahong #flower ...)
    text = re.sub(r'#\S+', '', text)
    
    # 5. Remove phone numbers (phòng trường hợp shop để SĐT ngay trong đoạn văn mở đầu)
    text = re.sub(r'(?:0|\+84)(?:\s|\.|-)?\d{2,3}(?:\s|\.|-)?\d{3}(?:\s|\.|-)?\d{3,4}', '', text)
    
    # 6. Clean extra spaces and empty lines
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def process_and_clean_tiktok_data():
    # Sử dụng pattern để tìm các file data tiktok raw
    dataset_dir = r"Dataset/Raw"
    # Tìm có thể là file Tiktok_data_Raw.csv hoặc các file dataset_tiktok...
    csv_files = glob.glob(os.path.join(dataset_dir, "Tiktok_data_Raw*.csv")) + \
                glob.glob(os.path.join("Dataset", "dataset_tiktok*.csv"))
    
    if not csv_files:
        print("Không tìm thấy file TikTok CSV nào!")
        return
        
    print(f"Tìm thấy {len(csv_files)} file. Bắt đầu gộp và làm sạch...")
    
    df_list = []
    for f in csv_files:
        try:
            temp_df = pd.read_csv(f, low_memory=False)
            df_list.append(temp_df)
            print(f" - Đã đọc: {os.path.basename(f)} ({len(temp_df)} dòng)")
        except Exception as e:
            print(f"Lỗi đọc file {f}: {e}")
            
    if not df_list:
        return
        
    df = pd.concat(df_list, ignore_index=True)
    
    # Các cột cần giữ lại
    columns_mapping = {
        'webVideoUrl': 'Video_URL',
        'authorMeta.name': 'Author',
        'text': 'Caption',
        'playCount': 'Views',
        'diggCount': 'Likes',
        'commentCount': 'Comments',
        'shareCount': 'Shares',
        'collectCount': 'Saves',
        'createTimeISO': 'Published_At',
        'videoMeta.duration': 'Duration'
    }
    
    # Giữ lại các cột có trong dataset và đổi tên
    actual_cols = [col for col in columns_mapping.keys() if col in df.columns]
    df_clean = df[actual_cols].rename(columns={col: columns_mapping[col] for col in actual_cols}).copy()
    
    # Xoá trùng lặp nếu có Video_URL
    if 'Video_URL' in df_clean.columns:
        df_clean = df_clean.drop_duplicates(subset=['Video_URL'])
    else:
        df_clean = df_clean.drop_duplicates()
    
    # TÁCH HASHTAG TỪ CAPTION
    def extract_hashtags(text):
        if pd.isna(text):
            return ""
        return " ".join(re.findall(r'#\S+', str(text)))
        
    print("Trích xuất hashtags từ Caption...")
    if 'Caption' in df_clean.columns:
        df_clean['Tags'] = df_clean['Caption'].apply(extract_hashtags)
        
    # Clean the caption text
    if 'Caption' in df_clean.columns:
        print("Làm sạch Caption...")
        df_clean['Caption'] = df_clean['Caption'].apply(clean_caption_text)
    
    print(f"Tiktok data cleaned successfully! Các cột hiện có ({len(df_clean.columns)}): {list(df_clean.columns)}")
    print("--- SAMPLE TIKTOK DATA ---")
    print(df_clean.head(2))
    print("-" * 50)
    
    # Lưu file đã làm sạch ra định dạng Excel
    output_dir = 'Dataset/Clean'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Tiktok_data_cleaned.xlsx')
    
    df_clean.to_excel(output_path, index=False)
    print(f"Đã lưu file làm sạch tại: {output_path}")

if __name__ == '__main__':
    process_and_clean_tiktok_data()
