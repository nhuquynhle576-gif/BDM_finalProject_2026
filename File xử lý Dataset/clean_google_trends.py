import pandas as pd
import os

def clean_google_trends():
    file_path = r'Dataset/Raw/Google_Trends_Raw.csv'
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    print(f"Bắt đầu đọc file: {file_path}")
    df = pd.read_csv(file_path)
    
    # Check current structure
    print("Cấu trúc hiện tại:")
    print(df.head())
    
    # Pivot the table to make 'Target_Flower' values into columns and 'Google_Trend_Score' into values
    # Each row will be a unique 'date'
    print("Converting to column format...")
    df_pivoted = df.pivot_table(index='date', columns='Target_Flower', values='Google_Trend_Score', aggfunc='first').reset_index()
    
    # Remove the index name from pivoting
    df_pivoted.columns.name = None
    
    print(f"Google Trends data converted successfully! Các cột hiện có ({len(df_pivoted.columns)}): {list(df_pivoted.columns)}")
    print("--- SAMPLE MỚI ---")
    print(df_pivoted.head(2))
    print("-" * 50)
    
    # Lưu file dưới dạng Excel
    output_dir = 'Dataset/Clean'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Google_Trends_cleaned.xlsx')
    
    df_pivoted.to_excel(output_path, index=False)
    print(f"Đã lưu file tại: {output_path}")

if __name__ == '__main__':
    clean_google_trends()
