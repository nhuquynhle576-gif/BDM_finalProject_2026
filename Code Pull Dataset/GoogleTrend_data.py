# ==========================================
# CELL 1: GOOGLE TRENDS SAFE SCRAPER
# ==========================================
from serpapi import GoogleSearch
import pandas as pd
import time
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Danh sách đầy đủ 60+ loại hoa
flower_list = [
    'rose', 'tulip', 'orchid', 'sunflower', 'peony', 'hydrangea', 'lily', 'daisy',
    'carnation', 'chrysanthemum', 'lavender', 'marigold', 'poppy', 'lotus', 'jasmine',
    'violet', 'begonia', 'camellia', 'clematis', 'crocus', 'daffodil', 'dahlia',
    'dandelion', 'freesia', 'geranium', 'gladiolus', 'heather', 'hibiscus', 'hyacinth',
    'iris', 'lilac', 'magnolia', 'morning glory', 'narcissus', 'pansy', 'petunia',
    'poinsettia', 'primrose', 'rhododendron', 'snapdragon', 'snowdrop', 'sweet pea',
    'verbena', 'water lily', 'zinnia', 'aster', 'azalea', 'baby breath', 'bellflower',
    'bird of paradise', 'bougainvillea', 'buttercup', 'calendula', 'columbine',
    'cornflower', 'cosmos', 'delphinium', 'forget me not', 'foxglove', 'gerbera'
]

def scrape_google_trends(keywords):
    csv_file = 'Google_Trends_Raw.csv'
    
    # Kiểm tra xem đã có dữ liệu từ trước chưa để chạy tiếp (resume)
    downloaded_flowers = []
    if os.path.exists(csv_file):
        try:
            df_existing = pd.read_csv(csv_file)
            if 'Target_Flower' in df_existing.columns:
                downloaded_flowers = df_existing['Target_Flower'].unique().tolist()
                logging.info(f"-> Đã tải {len(downloaded_flowers)} loại hoa trước đó. Bỏ qua để chạy tiếp tục...")
        except Exception:
            pass

    keywords_to_scrape = [fw for fw in keywords if fw not in downloaded_flowers]
    
    if not keywords_to_scrape:
        logging.info("🎉 Đã tải xong toàn bộ dữ liệu!")
        return

    for i, flower in enumerate(keywords_to_scrape):
        try:
            params = {
              "engine": "google_trends",
              "q": flower,
              "data_type": "TIMESERIES",
              "date": "today 12-m",
              "api_key": SERPAPI_KEY
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "interest_over_time" in results and results["interest_over_time"]["timeline_data"]:
                timeline_data = results["interest_over_time"]["timeline_data"]
                
                # Chuyển đổi JSON list thành dict cho DataFrame
                records = []
                for item in timeline_data:
                    date = item.get("date")
                    # Value trong timeline_data của SerpApi nằm trong danh sách values
                    values = item.get("values", [])
                    if values:
                        score = values[0].get("extracted_value", 0)
                        records.append({"date": date, "Target_Flower": flower, "Google_Trend_Score": score})
                
                df = pd.DataFrame(records)
                
                if not df.empty:
                    # Chuyển đổi date format nếu cần (SerpApi trả về dạng 'Feb 25, 2024')
                    try:
                        df['date'] = pd.to_datetime(df['date'])
                    except:
                        pass
                        
                    # Ghi nối dữ liệu vào file CSV
                    header = not os.path.exists(csv_file)
                    df.to_csv(csv_file, mode='a', header=header, index=False)
                    logging.info(f"✅ [{i+1}/{len(keywords_to_scrape)}] Tải thành công: {flower}")
                else:
                    logging.info(f"⚠️ [{i+1}/{len(keywords_to_scrape)}] Không có dữ liệu: {flower}")
            else:
                 logging.info(f"⚠️ [{i+1}/{len(keywords_to_scrape)}] Không có dữ liệu interest_over_time cho: {flower}")
                 if "error" in results:
                     logging.info(f"   Lỗi SerpApi: {results['error']}")
            
            # Rate limit của SerpApi khá thoải mái, nhưng cứ nghỉ 1 giây cho an toàn
            time.sleep(1)
            
        except Exception as e:
            logging.error(f"❌ Lỗi khi tải {flower}: {e}")

# Thực thi
scrape_google_trends(flower_list)