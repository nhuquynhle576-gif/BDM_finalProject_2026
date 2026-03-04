# 🌸 Trend-Based Flower Recommendation System Using Social Media Data

## 📋 Overview
This project builds a **Trend-Based Flower Recommendation System** that analyzes social media data to identify flower trends and provide data-driven recommendations for florist businesses.

The system collects data from social media platforms (YouTube, Reddit), processes it through a machine learning pipeline, and outputs actionable flower import recommendations based on current trends.

## 🎯 Objectives
- **Data Collection**: Gather flower-related content from social media using official APIs
- **Trend Forecasting**: Predict future interest levels for different flower types using time-series analysis
- **Recommendation Engine**: Suggest which flowers to import/stock based on trending data
- **Explainable AI (XAI)**: Use SHAP to explain model predictions with clear feature attribution

## 🏗️ System Architecture

```
Social Media APIs ──→ Data Collection ──→ Preprocessing & Feature Engineering
                                                      │
                                                      ▼
                                          ┌──────────────────────┐
                                          │   Feature Vectors:   │
                                          │  • Frequency         │
                                          │  • Growth Rate       │
                                          │  • Seasonality       │
                                          │  • Sentiment         │
                                          │  • Event Indicators  │
                                          └──────────┬───────────┘
                                                     │
                                    ┌────────────────┼────────────────┐
                                    ▼                                 ▼
                           Trend Forecasting              Recommendation System
                          (Random Forest, LR)           (Weighted Scoring Model)
                                    │                                 │
                                    ▼                                 ▼
                              SHAP / XAI                   Import Recommendations
                          (Feature Explanation)          (HIGH / MEDIUM / LOW priority)
```

## 📂 Project Structure

```
BDM/
├── README.md                          # Project documentation
├── get_data.py                        # YouTube data collection (basic)
├── get_data_expanded.py               # YouTube data collection (expanded, 35+ keywords)
├── get_reddit_data.py                 # Reddit data collection
├── implementation.py                  # Full ML pipeline implementation
├── flower_social_data.csv             # YouTube dataset (basic)
├── flower_social_data_expanded.csv    # YouTube dataset (expanded)
└── reddit_flower_data.csv             # Reddit dataset
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Data Collection | YouTube Data API v3, Reddit API (PRAW) |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn (Random Forest, Linear Regression) |
| NLP / Sentiment | TextBlob |
| Explainability | SHAP |
| Visualization | Matplotlib, Seaborn |

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/BDM.git
cd BDM

# Install dependencies
pip install google-api-python-client pandas scikit-learn matplotlib seaborn shap textblob praw
```

## 🚀 Usage

### 1. Data Collection

```bash
# Collect YouTube data (expanded)
python get_data_expanded.py

# Collect Reddit data (requires Reddit API credentials)
python get_reddit_data.py
```

### 2. Run Full Pipeline

```bash
python implementation.py
```

## 📊 Data Sources

| Platform | Method | Status |
|----------|--------|--------|
| YouTube | Official API v3 | ✅ Active |
| Reddit | Official API (PRAW) | ✅ Active |

> **Note**: This project uses only **official APIs** with proper authentication for data collection, ensuring reproducibility and compliance with platform terms of service.

## 📈 Features Engineered

| Feature | Description |
|---------|-------------|
| Frequency | Number of posts/videos mentioning a flower type per time period |
| Growth Rate | Month-over-month change in mention frequency |
| Seasonality | Cyclical encoding of monthly patterns (sin/cos) |
| Sentiment | Public opinion polarity from text analysis (TextBlob) |
| Event Indicators | Detection of related events (wedding, valentine, christmas, etc.) |
| Engagement Score | Composite metric from views, likes, comments |

## 📄 License
This project is for **academic research purposes only**.

## 👥 Team
- Academic Project - Big Data Management Course
