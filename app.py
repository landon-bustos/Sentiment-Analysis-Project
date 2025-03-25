import streamlit as st
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from urllib.parse import urljoin
import time
from datetime import datetime

st.set_page_config(
    page_title="Amazon Review Sentiment Analyzer",
    layout="wide"
)

st.title("Amazon Review Sentiment Analyzer")

st.markdown("""
### How to Use
1. Go to Amazon.com and find your product
2. Copy the product URL from your browser
3. Paste it below and click 'Analyze Reviews'

#### URL Format Examples:
```
Valid Link: https://www.amazon.com/dp/B0D1XD1ZV3
Valid Link: https://www.amazon.com/Apple-AirPods-Pro-2nd-Generation/dp/B0D1XD1ZV3
Invalid Link: https://www.amazon.com/s?k=airpods (search results page)
```
""")

def clean_amazon_url(url):
    try:
        if '?' in url:
            url = url.split('?')[0]
            
        if '/ref=' in url:
            url = url.split('/ref=')[0]
            
        return url
    except Exception as e:
        st.error(f"Error cleaning URL: {str(e)}")
        return None

def scrape_reviews(url):
    reviews = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': 'i18n-prefs=USD; session-id=123-1234567-1234567'
    }

    try:
        clean_url = clean_amazon_url(url)
        if not clean_url:
            return []
            
        st.info(f"Fetching reviews from: {clean_url}")
        response = requests.get(clean_url, headers=headers)
        
        if response.status_code != 200:
            st.error(f"Failed to fetch reviews. Status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        if 'Robot Check' in soup.get_text():
            st.error("Amazon is blocking our request. Please try again later.")
            return []
            
        review_texts = soup.find_all("span", class_="review-text")
        if not review_texts:
            review_texts = soup.find_all("span", {"data-hook": "review-body"})
            
        if not review_texts:
            st.warning("No reviews found on the page. This might be due to:")
            st.write("1. The product is new and has no reviews")
            st.write("2. Amazon's anti-bot protection is active")
            st.write("3. The URL might not be correct")
            return []
            
        review_ratings = soup.find_all("i", class_="review-rating")
        if not review_ratings:
            review_ratings = soup.find_all("i", {"data-hook": "review-star-rating"})
            
        review_dates = soup.find_all("span", {"data-hook": "review-date"})
        if not review_dates:
            review_dates = soup.find_all("span", class_="review-date")
            
        max_reviews = min(len(review_texts), len(review_ratings))
        
        for i in range(max_reviews):
            try:
                text = review_texts[i].get_text(separator="\n").strip()
                if not text:
                    continue
                    
                rating_text = review_ratings[i].get_text().strip()
                try:
                    rating = int(rating_text.split('.')[0])
                except:
                    continue
                    
                date = review_dates[i].get_text().strip() if i < len(review_dates) else ""
                
                reviews.append({
                    'text': text,
                    'rating': rating,
                    'date': date
                })
            except Exception as e:
                st.warning(f"Error extracting review: {str(e)}")
                continue
                
    except Exception as e:
        st.error(f"Error scraping reviews: {str(e)}")
    
    return reviews

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    return sentiment['compound']

def get_sentiment_label(score):
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"

url = st.text_input("Enter Amazon Product URL (product page or reviews page)")

if url:
    if st.button("Analyze Reviews"):
        with st.spinner("Scraping and analyzing reviews..."):
            reviews = scrape_reviews(url)
            
            if reviews:
                df = pd.DataFrame(reviews)
                
                df['sentiment_score'] = df['text'].apply(analyze_sentiment)
                df['sentiment'] = df['sentiment_score'].apply(get_sentiment_label)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Reviews", len(df))
                
                with col2:
                    avg_sentiment = df['sentiment_score'].mean()
                    st.metric("Average Sentiment", f"{avg_sentiment:.2f}")
                
                with col3:
                    avg_rating = df['rating'].mean()
                    st.metric("Average Rating", f"{avg_rating:.1f}/5")
                
                st.subheader("Sentiment Distribution")
                fig = px.pie(df, names='sentiment', title='Review Sentiment Distribution')
                st.plotly_chart(fig)
                
                st.subheader("Rating vs Sentiment")
                fig = px.box(df, x='rating', y='sentiment_score', title='Rating vs Sentiment Score')
                st.plotly_chart(fig)
                
                st.subheader("Reviews")
                df_display = df[['text', 'rating', 'sentiment', 'sentiment_score']].copy()
                df_display['sentiment_score'] = df_display['sentiment_score'].round(3)
                st.dataframe(
                    df_display,
                    column_config={
                        "text": "Review Text",
                        "rating": st.column_config.NumberColumn("Rating", format="%d⭐"),
                        "sentiment": "Sentiment",
                        "sentiment_score": "Sentiment Score"
                    }
                )
            else:
                st.error("No reviews found. Please check the URL and try again.")

with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Enter an Amazon product URL
    2. Click "Analyze Reviews"
    3. Wait for the analysis to complete
    
    **Note**: For best results, use:
    - Product detail pages
    - Reviews pages
    - URLs from amazon.com
    """)
    
    st.header("About")
    st.markdown("""
    This tool analyzes Amazon product reviews using:
    - VADER Sentiment Analysis
    - Selenium for web scraping
    - Plotly for visualizations
    """)
