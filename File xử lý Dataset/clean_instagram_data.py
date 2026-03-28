import pandas as pd
import os
import re
import emoji
import unicodedata

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
        text = text[:match.start()]
    
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

def clean_instagram_data():
    file_path = 'Dataset/Instagram_data.csv'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    df = pd.read_csv(file_path, low_memory=False)
    
    # Base columns to keep
    base_keep = ['caption', 'likesCount', 'commentsCount', 'ownerUsername']
    
    # Add hashtag columns (0 to 12)
    hashtag_cols = [f'hashtags/{i}' for i in range(13)]
    
    keep_cols = base_keep + hashtag_cols
    
    # Keep only those that actually exist
    actual_keep = [c for c in keep_cols if c in df.columns]
    
    df_clean = df[actual_keep].copy()
    
    # Gom các cột hashtag vào 1 cột Tags duy nhất y như Youtube
    hashtag_cols_actual = [c for c in hashtag_cols if c in df_clean.columns]
    if hashtag_cols_actual:
        print("Merging hashtags to a single column on Instagram data...")
        # Lọc ra các hashtag không rỗng, bỏ qua NaN
        df_clean['Tags'] = df_clean[hashtag_cols_actual].apply(
            lambda row: ' '.join(['#' + str(val) for val in row.dropna() if str(val).strip() != '']), 
            axis=1
        )
        # Xóa các cột hashtags/i lẻ tẻ
        df_clean = df_clean.drop(columns=hashtag_cols_actual)
    
    # Clean the caption column
    if 'caption' in df_clean.columns:
        print("Cleaning caption text on Instagram data...")
        df_clean['caption'] = df_clean['caption'].apply(clean_caption_text)
    
    output_dir = 'Dataset/Clean'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Instagram_data_cleaned.xlsx')
    df_clean.to_excel(output_path, index=False)
    
    print(f"Instagram data cleaned successfully! Saved to {output_path}")

if __name__ == '__main__':
    print("Cleaning Instagram dataset...")
    clean_instagram_data()
    print("Done!")
