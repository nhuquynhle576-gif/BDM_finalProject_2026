# 🌸 BDM Final Project 2026 — Flower Trend Analysis

> **Big Data Management** — Phân tích xu hướng hoa (Flower Trend Analysis) trên nhiều nền tảng mạng xã hội và công cụ tìm kiếm.

---

## 📖 Mô tả dự án

Dự án thu thập và phân tích dữ liệu về **xu hướng hoa** (flower trends) từ nhiều nguồn khác nhau bao gồm:

| Nguồn dữ liệu | Mô tả |
|---|---|
| 🎥 **YouTube** | Video về cắm hoa, xu hướng hoa, thiết kế hoa theo mùa/sự kiện |
| 📊 **Google Trends** | Chỉ số tìm kiếm (Interest over Time) cho 60+ loại hoa |
| 📸 **Instagram** | Bài đăng từ các tài khoản bán hoa, cắm hoa |
| 🎵 **TikTok** | Video ngắn về xu hướng hoa, bouquet, floral design |
| 👥 **Facebook Groups** | Bài viết từ các nhóm cộng đồng yêu hoa |

**Mục tiêu:** Xác định loại hoa nào đang trending, phân tích theo mùa/sự kiện, và tìm hiểu xu hướng thị trường hoa năm 2024–2025.

---

## 📁 Cấu trúc thư mục

```
BDM Code/
│
├── Code Pull Dataset/             # Script thu thập dữ liệu thô
│   ├── GoogleTrend_data.py        #   → Lấy dữ liệu Google Trends qua SerpAPI
│   └── Youtube_data.py            #   → Lấy dữ liệu YouTube qua YouTube Data API v3
│
├── File xử lý Dataset/            # Script làm sạch & xử lý dữ liệu
│   ├── clean_google_trends.py     #   → Pivot bảng Google Trends theo loại hoa
│   ├── clean_instagram_data.py    #   → Làm sạch caption, gộp hashtag Instagram
│   ├── clean_tiktok_data.py       #   → Làm sạch caption, trích hashtag TikTok
│   ├── clean_youtube_data.py      #   → Làm sạch title/description YouTube
│   └── merge_ig_data.py           #   → Gộp nhiều file CSV Instagram thành 1
│
├── Dataset/
│   ├── Raw/                       # Dữ liệu thô (CSV)
│   │   ├── Google_Trends_Raw.csv
│   │   ├── Instagram_data_Raw.csv
│   │   ├── Tiktok_data_Raw.csv
│   │   └── Youtube_data_Raw.csv
│   │
│   └── Clean/                     # Dữ liệu đã làm sạch (Excel)
│       ├── Google_Trends_data_cleaned.xlsx
│       ├── Instagram_data_cleaned.xlsx
│       ├── Tiktok_data_cleaned.xlsx
│       └── Youtube_data_cleaned.xlsx
│
├── get_data_expanded.py           # Script mở rộng thu thập YouTube (30+ keywords, pagination)
├── convert_json_to_csv.py         # Chuyển đổi JSON Facebook → CSV
├── convert_json_to_excel.py       # Chuyển đổi JSON Facebook → Excel (có format)
├── BDM_draft.ipynb                # Notebook phân tích & khám phá dữ liệu
├── Facebook_data_Raw.csv          # Dữ liệu thô Facebook Groups
├── .env                           # API keys (YouTube, SerpAPI) — KHÔNG PUSH LÊN GIT
└── README.md
```

---

## 🔧 Công nghệ & API sử dụng

| Công nghệ | Mục đích |
|---|---|
| **Python 3.x** | Ngôn ngữ chính |
| **pandas** | Xử lý & phân tích dữ liệu |
| **YouTube Data API v3** | Thu thập dữ liệu video YouTube |
| **SerpAPI** | Thu thập dữ liệu Google Trends |
| **Apify** | Scrape dữ liệu Instagram & TikTok |
| **openpyxl** | Xuất dữ liệu ra định dạng Excel |
| **emoji** | Loại bỏ emoji khỏi text |
| **python-dotenv** | Quản lý biến môi trường (.env) |

---

## 🚀 Hướng dẫn cài đặt & chạy

### 1. Clone repository

```bash
git clone https://github.com/nhuquynhle576-gif/BDM_finalProject_2026.git
cd BDM_finalProject_2026
```

### 2. Tạo môi trường ảo & cài đặt thư viện

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install pandas google-api-python-client google-search-results python-dotenv openpyxl emoji
```

### 3. Cấu hình API Keys

Tạo file `.env` ở thư mục gốc với nội dung:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
SERPAPI_KEY=your_serpapi_key_here
```

### 4. Thu thập dữ liệu

```bash
# Thu thập dữ liệu YouTube
python "Code Pull Dataset/Youtube_data.py"

# Thu thập dữ liệu Google Trends
python "Code Pull Dataset/GoogleTrend_data.py"
```

### 5. Làm sạch dữ liệu

```bash
python "File xử lý Dataset/clean_youtube_data.py"
python "File xử lý Dataset/clean_instagram_data.py"
python "File xử lý Dataset/clean_tiktok_data.py"
python "File xử lý Dataset/clean_google_trends.py"
```

---

## 📊 Quy trình xử lý dữ liệu (Data Pipeline)

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Thu thập dữ   │     │   Làm sạch &     │     │   Phân tích &   │
│   liệu thô     │ ──▶ │   Chuyển đổi     │ ──▶ │   Trực quan     │
│   (API/Scrape)  │     │   (Clean/Merge)  │     │   (Notebook)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
      │                        │                        │
  YouTube API             Loại bỏ emoji            BDM_draft.ipynb
  SerpAPI                 Loại bỏ hashtag
  Apify                   Chuẩn hóa Unicode
  Facebook Scraper        Xóa thông tin liên hệ
                          Gộp & xóa trùng lặp
```

---

## 🧹 Chi tiết xử lý dữ liệu

Các bước làm sạch text được áp dụng cho **Instagram, TikTok, YouTube**:

1. **Chuẩn hóa Unicode** — Chuyển đổi font chữ kiểu (ví dụ: `𝐓𝐈𝐄̣̂𝐌 𝐇𝐎𝐀` → `TIỆM HOA`)
2. **Cắt phần quảng cáo** — Loại bỏ phần sau các đường kẻ phân cách (`---`, `===`)
3. **Loại bỏ thông tin liên hệ** — Xóa các phần chứa Hotline, Zalo, địa chỉ, SĐT...
4. **Loại bỏ emoji** — Xóa toàn bộ emoji để text sạch hơn
5. **Loại bỏ hashtag** — Trích hashtag riêng ra cột `Tags` trước khi xóa khỏi text
6. **Xóa số điện thoại** — Pattern matching cho SĐT Việt Nam
7. **Dọn khoảng trắng** — Loại bỏ dòng trống và khoảng trắng thừa

---

## 🔑 Từ khóa tìm kiếm chính

Dự án sử dụng **30+ từ khóa** được phân loại theo:

- **Xu hướng chung:** `flower arrangement trends 2025`, `wedding flower trends`...
- **Theo loại hoa:** `rose bouquet`, `tulip arrangement`, `orchid decoration`, `peony wedding`...
- **Theo sự kiện:** `valentine flowers`, `wedding bouquet`, `birthday flower`, `graduation bouquet`...
- **Theo phong cách:** `minimalist arrangement`, `luxury floral`, `dried flower`, `boho wedding`...
- **Thị trường:** `flower shop business`, `floral industry trends`, `best selling flowers`...

---

## 👥 Thành viên nhóm

| Họ tên | GitHub |
|---|---|
| Như Quỳnh Lê | [@nhuquynhle576-gif](https://github.com/nhuquynhle576-gif) |

---

## 📝 Ghi chú

- File `.env` chứa API keys **không được push lên GitHub**. Hãy đảm bảo file `.gitignore` bao gồm `.env`.
- Dữ liệu Instagram và TikTok được thu thập qua **Apify** (không có script trực tiếp trong repo, sử dụng web interface).
- Dữ liệu Facebook được thu thập qua **Apify Facebook Groups Scraper** và chuyển đổi từ JSON sang CSV/Excel.

---

## 📄 License

Dự án này được thực hiện cho mục đích học tập trong môn **Big Data Management (BDM)**.
