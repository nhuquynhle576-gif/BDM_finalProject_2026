import pandas as pd
import glob
import os

def merge_instagram_datasets(input_pattern, output_file):
    print(f"Đang tìm kiếm các file dataset với pattern: {input_pattern}")
    csv_files = glob.glob(input_pattern)
    
    if not csv_files:
        print("Không tìm thấy file dataset Instagram nào.")
        return

    print(f"Tìm thấy {len(csv_files)} file. Bắt đầu gộp dữ liệu...")
    
    df_list = []
    for file in csv_files:
        try:
            # Apify thường xuất ra file CSV với newline/characters linh tinh, nên thêm config on_bad_lines nếu cần
            df = pd.read_csv(file, low_memory=False)
            df_list.append(df)
            print(f" - Đã đọc: {os.path.basename(file)} ({len(df)} dòng)")
        except Exception as e:
            print(f"Lỗi khi đọc file {file}: {e}")

    # Gộp tất cả DataFrames
    merged_df = pd.concat(df_list, ignore_index=True)
    
    print(f"\nTổng số dòng trước khi xóa trùng lặp: {len(merged_df)}")
    
    # Xóa trùng lặp dựa trên URL hoặc id của bài viết (nếu có cột 'url' hoặc 'id')
    # Ở đây dùng hàm drop_duplicates mặc định, hoặc chỉ định cột khóa chính nếu biết.
    if 'url' in merged_df.columns:
        merged_df = merged_df.drop_duplicates(subset=['url'])
    elif 'id' in merged_df.columns:
        merged_df = merged_df.drop_duplicates(subset=['id'])
    else:
        merged_df = merged_df.drop_duplicates()
        
    print(f"Tổng số dòng sau khi xóa trùng lặp: {len(merged_df)}")
    
    # Điền giá trị na bằng rỗng cho các cột text hoặc 0 cho cột số để xử lý an toàn
    if 'caption' in merged_df.columns:
        merged_df['caption'] = merged_df['caption'].fillna("")

    # Lưu ra file mới
    merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n[THÀNH CÔNG] Đã lưu dữ liệu gộp vào file: {output_file}")

if __name__ == "__main__":
    # Pattern để bắt các file CSV từ Apify Instagram Scraper trong thư mục gốc
    input_pattern = "dataset_instagram-scraper_*.csv"
    output_filename = "merged_instagram_data.csv"
    
    merge_instagram_datasets(input_pattern, output_filename)
