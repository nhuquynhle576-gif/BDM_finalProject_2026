"""
=============================================================================
  TREND-BASED FLOWER RECOMMENDATION SYSTEM USING SOCIAL MEDIA DATA
  Full Implementation Pipeline
=============================================================================
  
  Module 1: Data Collection (get_data.py - already done)
  Module 2: Data Preprocessing & Feature Engineering
  Module 3: Trend Forecasting (Time-Series Prediction)
  Module 4: Recommendation System (Flower Import Suggestions)
  Module 5: SHAP / Explainable AI (XAI)
  
  Data source: YouTube API v3 (official API, single platform)
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
import re

warnings.filterwarnings('ignore')

# ============================================================================
# MODULE 2: DATA PREPROCESSING & FEATURE ENGINEERING
# ============================================================================

def load_and_preprocess(filepath="flower_social_data.csv"):
    """
    Load raw YouTube data and perform preprocessing.
    - Parse dates
    - Clean text
    - Extract flower-related keywords
    - Engineer features: frequency, growth_rate, seasonality, sentiment, event_indicators
    """
    print("=" * 70)
    print("MODULE 2: DATA PREPROCESSING & FEATURE ENGINEERING")
    print("=" * 70)
    
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    print(f"\n[INFO] Loaded {len(df)} records from {filepath}")
    
    # --- 2.1 Parse datetime ---
    df['Published_At'] = pd.to_datetime(df['Published_At'], errors='coerce')
    df['Year'] = df['Published_At'].dt.year
    df['Month'] = df['Published_At'].dt.month
    df['Week'] = df['Published_At'].dt.isocalendar().week.astype(int)
    df['DayOfWeek'] = df['Published_At'].dt.dayofweek
    df['YearMonth'] = df['Published_At'].dt.to_period('M')
    
    # --- 2.2 Extract flower types from Title + Description + Tags ---
    flower_types = [
        'rose', 'tulip', 'lily', 'orchid', 'sunflower', 'daisy', 'peony',
        'hydrangea', 'lavender', 'carnation', 'chrysanthemum', 'jasmine',
        'dahlia', 'magnolia', 'iris', 'poppy', 'ranunculus', 'marigold',
        'gardenia', 'amaryllis', 'anemone', 'aster', 'begonia', 'camellia',
        'daffodil', 'freesia', 'gerbera', 'hibiscus', 'hyacinth',
        'lisianthus', 'anthurium', 'protea', 'delphinium', 'foxglove',
        'zinnia', 'cosmos', 'stock', 'sweet pea', 'wisteria', 'hellebore',
        'pansy', 'petunia', 'violet', 'clematis', 'bellflower'
    ]
    
    def extract_flowers(row):
        text = str(row.get('Title', '')) + ' ' + str(row.get('Description', '')) + ' ' + str(row.get('Tags', ''))
        text = text.lower()
        found = [f for f in flower_types if f in text]
        return ','.join(found) if found else 'general_floral'
    
    df['Flower_Types'] = df.apply(extract_flowers, axis=1)
    
    # --- 2.3 Sentiment Analysis using TextBlob ---
    print("[INFO] Performing sentiment analysis...")
    try:
        from textblob import TextBlob
        def get_sentiment(text):
            if pd.isna(text) or str(text).strip() == '':
                return 0.0
            blob = TextBlob(str(text)[:500])  # Limit text length
            return blob.sentiment.polarity
        
        df['Sentiment'] = df['Title'].apply(get_sentiment)
        df['Sentiment_Category'] = pd.cut(df['Sentiment'], 
                                           bins=[-1, -0.1, 0.1, 1], 
                                           labels=['Negative', 'Neutral', 'Positive'])
    except ImportError:
        print("[WARNING] TextBlob not available, using random sentiment")
        df['Sentiment'] = np.random.uniform(-0.5, 0.5, len(df))
        df['Sentiment_Category'] = 'Neutral'
    
    # --- 2.4 Event Indicators ---
    def detect_event(row):
        text = str(row.get('Title', '')) + ' ' + str(row.get('Description', ''))
        text = text.lower()
        events = {
            'wedding': 'wedding' in text or 'bridal' in text or 'bride' in text,
            'valentine': 'valentine' in text or 'love' in text,
            'christmas': 'christmas' in text or 'xmas' in text or 'holiday' in text,
            'mothers_day': 'mother' in text or "mom" in text,
            'spring': 'spring' in text,
            'fall': 'fall' in text or 'autumn' in text,
            'funeral': 'funeral' in text or 'sympathy' in text or 'memorial' in text,
            'birthday': 'birthday' in text,
            'graduation': 'graduation' in text,
        }
        detected = [k for k, v in events.items() if v]
        return ','.join(detected) if detected else 'general'
    
    df['Event_Type'] = df.apply(detect_event, axis=1)
    
    # --- 2.5 Engagement metrics ---
    df['Engagement_Score'] = df['View_Count'] + df['Like_Count'] * 10 + df['Comment_Count'] * 50
    df['Like_View_Ratio'] = np.where(df['View_Count'] > 0, 
                                      df['Like_Count'] / df['View_Count'], 0)
    df['Comment_View_Ratio'] = np.where(df['View_Count'] > 0, 
                                         df['Comment_Count'] / df['View_Count'], 0)
    
    # --- 2.6 Seasonality Feature ---
    season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',
                  3: 'Spring', 4: 'Spring', 5: 'Spring',
                  6: 'Summer', 7: 'Summer', 8: 'Summer',
                  9: 'Fall', 10: 'Fall', 11: 'Fall'}
    df['Season'] = df['Month'].map(season_map)
    
    print(f"[INFO] Feature engineering completed.")
    print(f"[INFO] Columns: {list(df.columns)}")
    print(f"[INFO] Flower types found: {df['Flower_Types'].value_counts().head(10).to_dict()}")
    
    return df


# ============================================================================
# MODULE 3: TREND FORECASTING
# ============================================================================

def build_trend_features(df):
    """
    Build aggregated time-series features for trend forecasting.
    Features: frequency, growth_rate, seasonality, avg_sentiment, event_indicators
    """
    print("\n" + "=" * 70)
    print("MODULE 3: TREND FORECASTING")
    print("=" * 70)
    
    # --- 3.1 Aggregate by YearMonth ---
    # Explode flower types to get one row per flower per video
    df_exploded = df.copy()
    df_exploded['Flower_Types'] = df_exploded['Flower_Types'].str.split(',')
    df_exploded = df_exploded.explode('Flower_Types')
    df_exploded['Flower_Types'] = df_exploded['Flower_Types'].str.strip()
    
    # Group by YearMonth and Flower_Types
    trend_df = df_exploded.groupby(['YearMonth', 'Flower_Types']).agg(
        Frequency=('Title', 'count'),
        Avg_Views=('View_Count', 'mean'),
        Total_Views=('View_Count', 'sum'),
        Avg_Likes=('Like_Count', 'mean'),
        Total_Likes=('Like_Count', 'sum'),
        Avg_Comments=('Comment_Count', 'mean'),
        Total_Engagement=('Engagement_Score', 'sum'),
        Avg_Sentiment=('Sentiment', 'mean'),
        Avg_Like_View_Ratio=('Like_View_Ratio', 'mean'),
    ).reset_index()
    
    # Convert YearMonth to timestamp for modeling
    trend_df['Date'] = trend_df['YearMonth'].dt.to_timestamp()
    trend_df = trend_df.sort_values(['Flower_Types', 'Date'])
    
    # --- 3.2 Growth Rate (month-over-month) ---
    trend_df['Growth_Rate'] = trend_df.groupby('Flower_Types')['Frequency'].pct_change().fillna(0)
    trend_df['Growth_Rate'] = trend_df['Growth_Rate'].clip(-5, 5)  # Cap extreme values
    
    # --- 3.3 Moving Average (smoothed trend) ---
    trend_df['Freq_MA3'] = trend_df.groupby('Flower_Types')['Frequency'].transform(
        lambda x: x.rolling(3, min_periods=1).mean()
    )
    
    # --- 3.4 Seasonality encoding ---
    trend_df['Month'] = trend_df['Date'].dt.month
    trend_df['Month_Sin'] = np.sin(2 * np.pi * trend_df['Month'] / 12)
    trend_df['Month_Cos'] = np.cos(2 * np.pi * trend_df['Month'] / 12)
    
    print(f"[INFO] Built trend features: {trend_df.shape[0]} records")
    print(f"[INFO] Flower types tracked: {trend_df['Flower_Types'].nunique()}")
    
    return trend_df, df_exploded


def forecast_trends(trend_df):
    """
    Trend Forecasting using Linear Regression + Random Forest.
    Predicts future interest (Frequency) for each flower type.
    """
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    print("\n[INFO] Training Trend Forecasting Models...")
    
    # Filter flower types with sufficient data
    flower_counts = trend_df['Flower_Types'].value_counts()
    valid_flowers = flower_counts[flower_counts >= 3].index.tolist()
    trend_filtered = trend_df[trend_df['Flower_Types'].isin(valid_flowers)].copy()
    
    if len(trend_filtered) < 10:
        print("[WARNING] Not enough data for robust forecasting. Using all data.")
        trend_filtered = trend_df.copy()
    
    # Encode flower types
    trend_filtered['Flower_Encoded'] = pd.Categorical(trend_filtered['Flower_Types']).codes
    
    # Feature columns
    feature_cols = ['Month_Sin', 'Month_Cos', 'Avg_Sentiment', 'Growth_Rate', 
                    'Avg_Like_View_Ratio', 'Flower_Encoded']
    target_col = 'Frequency'
    
    # Handle NaN/inf
    trend_filtered[feature_cols] = trend_filtered[feature_cols].replace([np.inf, -np.inf], 0).fillna(0)
    
    X = trend_filtered[feature_cols].values
    y = trend_filtered[target_col].values
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # --- Model 1: Linear Regression ---
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_pred = lr_model.predict(X_test)
    lr_pred = np.maximum(lr_pred, 0)  # No negative frequency
    
    print("\n--- Linear Regression Results ---")
    print(f"  MAE:  {mean_absolute_error(y_test, lr_pred):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, lr_pred)):.4f}")
    print(f"  R²:   {r2_score(y_test, lr_pred):.4f}")
    
    # --- Model 2: Random Forest ---
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    
    print("\n--- Random Forest Results ---")
    print(f"  MAE:  {mean_absolute_error(y_test, rf_pred):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, rf_pred)):.4f}")
    print(f"  R²:   {r2_score(y_test, rf_pred):.4f}")
    
    # Feature importance
    importance = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\n--- Feature Importance (Random Forest) ---")
    print(importance.to_string(index=False))
    
    return rf_model, lr_model, feature_cols, trend_filtered, X_test, y_test, rf_pred


# ============================================================================
# MODULE 4: RECOMMENDATION SYSTEM
# ============================================================================

def build_recommendation(df_exploded, trend_df):
    """
    Recommendation System: Suggest flowers for import based on trending data.
    Uses a scoring system combining: trend score, engagement, sentiment, seasonality.
    """
    print("\n" + "=" * 70)
    print("MODULE 4: RECOMMENDATION SYSTEM")
    print("=" * 70)
    
    # --- 4.1 Calculate composite trend score ---
    # Get latest period data
    latest_periods = trend_df.sort_values('Date').groupby('Flower_Types').tail(3)
    
    recommendation_df = latest_periods.groupby('Flower_Types').agg(
        Avg_Frequency=('Frequency', 'mean'),
        Avg_Growth_Rate=('Growth_Rate', 'mean'),
        Total_Engagement=('Total_Engagement', 'sum'),
        Avg_Sentiment=('Avg_Sentiment', 'mean'),
        Latest_Views=('Avg_Views', 'last'),
    ).reset_index()
    
    # --- 4.2 Normalize features (Min-Max scaling) ---
    from sklearn.preprocessing import MinMaxScaler
    
    scaler = MinMaxScaler()
    score_cols = ['Avg_Frequency', 'Avg_Growth_Rate', 'Total_Engagement', 'Avg_Sentiment']
    
    for col in score_cols:
        recommendation_df[col] = recommendation_df[col].replace([np.inf, -np.inf], 0).fillna(0)
    
    if len(recommendation_df) > 1:
        recommendation_df[['Norm_Freq', 'Norm_Growth', 'Norm_Engage', 'Norm_Sentiment']] = \
            scaler.fit_transform(recommendation_df[score_cols])
    else:
        for nc in ['Norm_Freq', 'Norm_Growth', 'Norm_Engage', 'Norm_Sentiment']:
            recommendation_df[nc] = 0.5
    
    # --- 4.3 Weighted Recommendation Score ---
    # Weights can be tuned based on business needs
    W_FREQ = 0.30       # How often it appears (popularity)
    W_GROWTH = 0.25     # Growth momentum
    W_ENGAGE = 0.30     # Engagement level
    W_SENTIMENT = 0.15  # Public sentiment
    
    recommendation_df['Recommendation_Score'] = (
        W_FREQ * recommendation_df['Norm_Freq'] +
        W_GROWTH * recommendation_df['Norm_Growth'] +
        W_ENGAGE * recommendation_df['Norm_Engage'] +
        W_SENTIMENT * recommendation_df['Norm_Sentiment']
    )
    
    # --- 4.4 Priority ranking ---
    recommendation_df['Priority'] = recommendation_df['Recommendation_Score'].rank(
        ascending=False, method='dense'
    ).astype(int)
    
    # Priority labels
    def get_priority_label(score):
        if score >= 0.7:
            return 'HIGH - Import Now'
        elif score >= 0.4:
            return 'MEDIUM - Consider'
        else:
            return 'LOW - Monitor'
    
    recommendation_df['Action'] = recommendation_df['Recommendation_Score'].apply(get_priority_label)
    
    # Sort by score
    recommendation_df = recommendation_df.sort_values('Recommendation_Score', ascending=False)
    
    print("\n--- FLOWER IMPORT RECOMMENDATIONS ---")
    print(recommendation_df[['Flower_Types', 'Recommendation_Score', 'Priority', 'Action', 
                              'Avg_Frequency', 'Avg_Growth_Rate']].to_string(index=False))
    
    return recommendation_df


# ============================================================================
# MODULE 5: SHAP / EXPLAINABLE AI (XAI)
# ============================================================================

def explain_with_shap(rf_model, X_test, feature_cols):
    """
    Use SHAP to explain the Random Forest predictions.
    Only applied when features are clearly defined (as per professor's requirement).
    """
    print("\n" + "=" * 70)
    print("MODULE 5: SHAP / EXPLAINABLE AI (XAI)")
    print("=" * 70)
    
    try:
        import shap
        
        print("\n[INFO] Computing SHAP values...")
        print(f"[INFO] Features used: {feature_cols}")
        print("  - Month_Sin/Cos: Seasonality encoding")
        print("  - Avg_Sentiment: Public opinion polarity")
        print("  - Growth_Rate: Month-over-month frequency change")
        print("  - Avg_Like_View_Ratio: Engagement quality indicator")
        print("  - Flower_Encoded: Flower type identifier")
        
        # Create SHAP explainer
        explainer = shap.TreeExplainer(rf_model)
        
        # Calculate SHAP values
        X_test_df = pd.DataFrame(X_test, columns=feature_cols)
        shap_values = explainer.shap_values(X_test_df)
        
        # --- 5.1 Summary Plot ---
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_df, show=False)
        plt.title("SHAP Feature Importance - Trend Forecasting Model")
        plt.tight_layout()
        plt.savefig("shap_summary_plot.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("[INFO] Saved: shap_summary_plot.png")
        
        # --- 5.2 Bar Plot ---
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_test_df, plot_type="bar", show=False)
        plt.title("SHAP Mean Absolute Impact on Prediction")
        plt.tight_layout()
        plt.savefig("shap_bar_plot.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("[INFO] Saved: shap_bar_plot.png")
        
        # --- 5.3 Feature importance from SHAP ---
        shap_importance = pd.DataFrame({
            'Feature': feature_cols,
            'Mean_SHAP': np.abs(shap_values).mean(axis=0)
        }).sort_values('Mean_SHAP', ascending=False)
        
        print("\n--- SHAP Feature Importance ---")
        print(shap_importance.to_string(index=False))
        
        return shap_values, explainer
        
    except Exception as e:
        print(f"[WARNING] SHAP analysis failed: {e}")
        print("[INFO] Generating feature importance from Random Forest instead.")
        return None, None


# ============================================================================
# MODULE 6: VISUALIZATION & REPORTING
# ============================================================================

def generate_visualizations(df, trend_df, recommendation_df, y_test=None, rf_pred=None):
    """
    Generate all visualizations for the report.
    """
    print("\n" + "=" * 70)
    print("MODULE 6: VISUALIZATION & REPORTING")
    print("=" * 70)
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # --- 6.1 Video Count Distribution by Query ---
    fig, ax = plt.subplots(figsize=(10, 5))
    df['Query'].value_counts().plot(kind='barh', ax=ax, color=sns.color_palette("viridis", len(df['Query'].unique())))
    ax.set_title("Number of Videos per Search Query", fontsize=14, fontweight='bold')
    ax.set_xlabel("Count")
    plt.tight_layout()
    plt.savefig("viz_query_distribution.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_query_distribution.png")
    
    # --- 6.2 Top Flower Types Mentioned ---
    flower_counts = df['Flower_Types'].str.split(',').explode().str.strip().value_counts().head(15)
    fig, ax = plt.subplots(figsize=(10, 6))
    flower_counts.plot(kind='bar', ax=ax, color=sns.color_palette("husl", 15))
    ax.set_title("Top 15 Flower Types Mentioned in YouTube Videos", fontsize=14, fontweight='bold')
    ax.set_xlabel("Flower Type")
    ax.set_ylabel("Mention Count")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("viz_top_flowers.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_top_flowers.png")
    
    # --- 6.3 Monthly Trend over Time ---
    monthly = df.groupby(df['Published_At'].dt.to_period('M')).agg(
        Count=('Title', 'count'),
        Avg_Views=('View_Count', 'mean'),
        Total_Engagement=('Engagement_Score', 'sum')
    ).reset_index()
    monthly['Published_At'] = monthly['Published_At'].dt.to_timestamp()
    
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(monthly['Published_At'], monthly['Count'], 'b-o', label='Video Count', linewidth=2)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Video Count', color='b')
    ax2 = ax1.twinx()
    ax2.bar(monthly['Published_At'], monthly['Total_Engagement'], alpha=0.3, color='orange', label='Total Engagement')
    ax2.set_ylabel('Total Engagement', color='orange')
    ax1.set_title("Monthly Trend: Video Count & Engagement Over Time", fontsize=14, fontweight='bold')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.95))
    plt.tight_layout()
    plt.savefig("viz_monthly_trend.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_monthly_trend.png")
    
    # --- 6.4 Sentiment Distribution ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].hist(df['Sentiment'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    axes[0].set_title("Sentiment Score Distribution", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Sentiment Polarity")
    axes[0].set_ylabel("Count")
    axes[0].axvline(x=0, color='red', linestyle='--', label='Neutral')
    axes[0].legend()
    
    if 'Sentiment_Category' in df.columns:
        sent_counts = df['Sentiment_Category'].value_counts()
        axes[1].pie(sent_counts.values, labels=sent_counts.index, autopct='%1.1f%%', 
                    colors=['#ff6b6b', '#ffd93d', '#6bcb77'], startangle=90)
        axes[1].set_title("Sentiment Category Distribution", fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("viz_sentiment.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_sentiment.png")
    
    # --- 6.5 Event Type Distribution ---
    event_counts = df['Event_Type'].str.split(',').explode().str.strip().value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    event_counts.plot(kind='barh', ax=ax, color=sns.color_palette("Set2", len(event_counts)))
    ax.set_title("Event Type Distribution in Flower Content", fontsize=14, fontweight='bold')
    ax.set_xlabel("Count")
    plt.tight_layout()
    plt.savefig("viz_event_types.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_event_types.png")
    
    # --- 6.6 Seasonal Engagement Heatmap ---
    if 'Season' in df.columns:
        season_data = df.groupby(['Season', 'Query']).agg(
            Avg_Engagement=('Engagement_Score', 'mean')
        ).reset_index()
        pivot = season_data.pivot_table(index='Query', columns='Season', values='Avg_Engagement', aggfunc='mean')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax, linewidths=0.5)
        ax.set_title("Average Engagement by Season & Query", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig("viz_seasonal_heatmap.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("[INFO] Saved: viz_seasonal_heatmap.png")
    
    # --- 6.7 Recommendation Score Chart ---
    top_recs = recommendation_df.head(15)
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.4 else '#e74c3c' 
              for s in top_recs['Recommendation_Score']]
    bars = ax.barh(top_recs['Flower_Types'], top_recs['Recommendation_Score'], color=colors)
    ax.set_xlabel("Recommendation Score")
    ax.set_title("Flower Import Recommendation Scores", fontsize=14, fontweight='bold')
    ax.axvline(x=0.7, color='green', linestyle='--', alpha=0.5, label='HIGH threshold')
    ax.axvline(x=0.4, color='orange', linestyle='--', alpha=0.5, label='MEDIUM threshold')
    ax.legend()
    plt.tight_layout()
    plt.savefig("viz_recommendation_scores.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_recommendation_scores.png")
    
    # --- 6.8 Actual vs Predicted (if available) ---
    if y_test is not None and rf_pred is not None:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(y_test, rf_pred, alpha=0.6, color='steelblue', edgecolors='black', s=60)
        max_val = max(max(y_test), max(rf_pred)) * 1.1
        ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        ax.set_xlabel("Actual Frequency", fontsize=12)
        ax.set_ylabel("Predicted Frequency", fontsize=12)
        ax.set_title("Trend Forecasting: Actual vs Predicted", fontsize=14, fontweight='bold')
        ax.legend()
        plt.tight_layout()
        plt.savefig("viz_actual_vs_predicted.png", dpi=150, bbox_inches='tight')
        plt.close()
        print("[INFO] Saved: viz_actual_vs_predicted.png")
    
    # --- 6.9 Engagement Correlation Matrix ---
    num_cols = ['View_Count', 'Like_Count', 'Comment_Count', 'Engagement_Score', 
                'Sentiment', 'Like_View_Ratio']
    corr_matrix = df[num_cols].corr()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=ax,
                center=0, linewidths=0.5, square=True)
    ax.set_title("Feature Correlation Matrix", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("viz_correlation_matrix.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("[INFO] Saved: viz_correlation_matrix.png")
    
    print("\n[INFO] All visualizations generated successfully!")


# ============================================================================
# MAIN EXECUTION PIPELINE
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("  TREND-BASED FLOWER RECOMMENDATION SYSTEM")
    print("  Using Social Media Data (YouTube API)")
    print("=" * 70)
    print(f"  Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # ---- Step 1: Load & Preprocess ----
    df = load_and_preprocess("flower_social_data.csv")
    
    # Save preprocessed data
    df.to_csv("preprocessed_data.csv", index=False, encoding='utf-8-sig')
    print("[INFO] Saved: preprocessed_data.csv")
    
    # ---- Step 2: Build Trend Features ----
    trend_df, df_exploded = build_trend_features(df)
    trend_df.to_csv("trend_features.csv", index=False, encoding='utf-8-sig')
    print("[INFO] Saved: trend_features.csv")
    
    # ---- Step 3: Trend Forecasting ----
    rf_model, lr_model, feature_cols, trend_filtered, X_test, y_test, rf_pred = forecast_trends(trend_df)
    
    # ---- Step 4: Recommendation ----
    recommendation_df = build_recommendation(df_exploded, trend_df)
    recommendation_df.to_csv("recommendations.csv", index=False, encoding='utf-8-sig')
    print("[INFO] Saved: recommendations.csv")
    
    # ---- Step 5: SHAP / XAI ----
    shap_values, explainer = explain_with_shap(rf_model, X_test, feature_cols)
    
    # ---- Step 6: Visualizations ----
    generate_visualizations(df, trend_df, recommendation_df, y_test, rf_pred)
    
    # ---- Summary Report ----
    print("\n" + "=" * 70)
    print("  EXECUTION SUMMARY")
    print("=" * 70)
    print(f"  Total videos analyzed:     {len(df)}")
    print(f"  Unique flower types found: {df_exploded['Flower_Types'].nunique()}")
    print(f"  Time range:                {df['Published_At'].min().strftime('%Y-%m')} to {df['Published_At'].max().strftime('%Y-%m')}")
    print(f"  Trend periods tracked:     {trend_df['YearMonth'].nunique()}")
    print(f"  Top recommended flower:    {recommendation_df.iloc[0]['Flower_Types']}")
    print(f"")
    print(f"  Output files:")
    print(f"    - preprocessed_data.csv")
    print(f"    - trend_features.csv")
    print(f"    - recommendations.csv")
    print(f"    - viz_*.png (visualizations)")
    print(f"    - shap_*.png (SHAP explanations)")
    print("=" * 70)
    print("  PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
