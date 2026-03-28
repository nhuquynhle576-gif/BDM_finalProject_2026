import json
import pandas as pd
import os

def convert_json_to_csv(json_path, csv_path):
    print(f"Reading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Use pandas json_normalize to flatten the nested structures (like 'user')
    # This will create columns like 'user.id', 'user.name'
    df = pd.json_normalize(data)
    
    # For columns that are still lists (like 'attachments'), 
    # we convert them to JSON strings to ensure they are saved in CSV
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            print(f"Serializing nested column: {col}")
            df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
    
    # Save to CSV
    print(f"Saving to {csv_path}...")
    # use utf-8-sig for better Excel compatibility with Vietnamese characters
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print("Done!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'dataset_facebook-groups-scraper_2026-03-19_14-54-43-576.json')
    output_file = os.path.join(current_dir, 'dataset_facebook-groups.csv')
    
    convert_json_to_csv(input_file, output_file)
