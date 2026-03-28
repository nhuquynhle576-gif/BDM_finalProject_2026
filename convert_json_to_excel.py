import json
import pandas as pd
import os

def convert_json_to_excel(json_path, excel_path):
    print(f"Reading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Use pandas json_normalize to flatten the nested structures
    df = pd.json_normalize(data)
    
    # For columns that are still lists/dicts, convert to JSON strings
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
            df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
    
    print(f"Saving to {excel_path}...")
    
    # Use ExcelWriter to apply some formatting
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Facebook Data')
        
        # Access the openpyxl workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Facebook Data']
        
        # Set some basic formatting
        # 1. Adjust column widths (capped at a reasonable value)
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter # Get the column name
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column].width = adjusted_width
            
        # 2. Enable Wrap Text for the 'text' column if it exists
        from openpyxl.styles import Alignment
        text_col_index = None
        for i, col_name in enumerate(df.columns):
            if col_name == 'text':
                text_col_index = i + 1
                break
        
        if text_col_index:
            col_letter = worksheet.cell(row=1, column=text_col_index).column_letter
            for cell in worksheet[col_letter]:
                cell.alignment = Alignment(wrapText=True, vertical='top')
            worksheet.column_dimensions[col_letter].width = 60 # Make text column wider
            
    print("Done!")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'dataset_facebook-groups-scraper_2026-03-19_14-54-43-576.json')
    output_file = os.path.join(current_dir, 'dataset_facebook-groups.xlsx')
    
    convert_json_to_excel(input_file, output_file)
