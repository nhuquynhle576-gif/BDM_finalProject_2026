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

def clean_youtube_data():
    file_path = 'Dataset/Youtube_data.csv'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    df = pd.read_csv(file_path)
    
    # Keep specific columns
    keep_cols = [
        'Video_ID', 'Channel_Title', 'Title', 'Description', 
        'Tags', 'View_Count', 'Like_Count', 'Published_At'
    ]
    # Keep only those that actually exist in the dataframe
    actual_keep = [c for c in keep_cols if c in df.columns]
    
    df_clean = df[actual_keep].copy()
    
    # === BƯỚC MỚI: TÁCH HASHTAG TỪ TITLE VÀ DESCRIPTION ===
    def extract_hashtags(text):
        if pd.isna(text):
            return ""
        return " ".join(re.findall(r'#\S+', str(text)))
        
    print("Extracting hashtags from Title and Description on Youtube data...")
    extracted_tags = pd.Series("", index=df_clean.index)
    if 'Title' in df_clean.columns:
        extracted_tags += " " + df_clean['Title'].apply(extract_hashtags)
    if 'Description' in df_clean.columns:
        extracted_tags += " " + df_clean['Description'].apply(extract_hashtags)
        
    # Gộp chung vào cột 'Tags' đã có sẵn của Youtube
    if 'Tags' in df_clean.columns:
        df_clean['Tags'] = df_clean['Tags'].fillna("") + extracted_tags
        df_clean['Tags'] = df_clean['Tags'].str.replace(r'\s+', ' ', regex=True).str.strip()
    else:
        df_clean['Tags'] = extracted_tags.str.strip()
    
    # Clean the title and description columns
    print("Cleaning title and description text on Youtube data...")
    if 'Title' in df_clean.columns:
        df_clean['Title'] = df_clean['Title'].apply(clean_caption_text)
    if 'Description' in df_clean.columns:
        df_clean['Description'] = df_clean['Description'].apply(clean_caption_text)
        
    output_dir = 'Dataset/Clean'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Youtube_data_cleaned.xlsx')
    df_clean.to_excel(output_path, index=False)
    
    print(f"Youtube data cleaned successfully! Saved to {output_path}")

if __name__ == '__main__':
    print("Cleaning Youtube dataset...")
    clean_youtube_data()
    print("Done!")
