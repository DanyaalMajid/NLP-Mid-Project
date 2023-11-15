import requests
import streamlit as st
import random
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import download
import datetime

# Download NLTK resources if not already downloaded
download('vader_lexicon')

# Function to load sources from CSV
def load_sources(csv_filename='sources.csv'):
    try:
        sources_df = pd.read_csv(csv_filename)
        return list(sources_df['Source'])
    except FileNotFoundError:
        st.warning(f"{csv_filename} not found. Run get_and_save_sources to fetch and save sources.")
        return None

# Function to perform sentiment analysis using NLTK Sentiment Analyzer
def analyze_sentiment(description):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(description)['compound']
    
    # Classify sentiment based on the compound score
    if sentiment_score >= 0.05:
        return 'Positive'
    elif sentiment_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

# Function to fetch news data and perform sentiment analysis
def fetch_and_analyze_news(query, api_key, date_from, date_to, selected_sources):
    url = 'https://newsapi.org/v2/everything'
    
    # Set up parameters
    parameters = {'q': query, 'apiKey': api_key}
    
    if date_from:
        parameters['from'] = date_from.strftime('%Y-%m-%d')
    if date_to:
        parameters['to'] = date_to.strftime('%Y-%m-%d')
    
    if selected_sources:
        parameters['sources'] = ','.join(selected_sources)
    
    response = requests.get(url, params=parameters)
    
    if response.status_code == 200:
        news_data = response.json()
        num_results = news_data['totalResults']
        
        # Initialize counters for positive and negative results
        positive_count = 0
        negative_count = 0
        
        # Store results for displaying some randomized results
        results_for_display = []
        sentiment_scores = []
        
        for article in news_data['articles']:
            description = article.get('description')  # Use get to handle potential None
            title = article.get('title')
            
            if description is not None:
                # Analyze sentiment
                sentiment = analyze_sentiment(description)
                
                # Count positive and negative results
                if sentiment == 'Positive':
                    positive_count += 1
                elif sentiment == 'Negative':
                    negative_count += 1

                # Store sentiment score
                sentiment_scores.append(sentiment)
                
                # Store results for display
                results_for_display.append({'title': title, 'description': description, 'sentiment': sentiment})

        overall_sentiment = analyze_sentiment(' '.join(sentiment_scores))
        
        return positive_count, negative_count, results_for_display, overall_sentiment, num_results
    
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None, None, None

# Streamlit app
st.title("News Sentiment Analysis App")

# Load sources from CSV
sources = load_sources()

# User input for the query
query = st.text_input("Enter your news query:")

# Calculate 29 days before today
min_date = datetime.date.today() - datetime.timedelta(days=29)

# User input for the 'from' date
date_from = st.date_input("Select From Date:", value=None, min_value=min_date, max_value=datetime.date.today())

# User input for the 'to' date
date_to = st.date_input("Select To Date:", value=None, min_value=min_date, max_value=datetime.date.today())

# User input for sources
selected_sources = st.multiselect("Select Sources:", sources)

# Button to trigger analysis
if st.button("Analyze Sentiment"):
    if query:
        # Replace 'YOUR_API_KEY' with your actual API key from the news service provider
        api_key = st.secrets["api_key"]
        
        positive_count, negative_count, results_for_display, overall_sentiment, num_results = fetch_and_analyze_news(query, api_key, date_from, date_to, selected_sources)
        
        print(f"Number of Positive Results: {positive_count}")
        print(f"Number of Negative Results: {negative_count}")
        print(f"Overall Sentiment: {overall_sentiment}")

        st.header("Analysis Results:")

        st.write(f"Number of Results: {num_results}")

        st.write("Analyzed Results: 100")
        
        st.write(f"Number of Positive Results: {positive_count}")

        st.write(f"Number of Negative Results: {negative_count}")

        st.write(f"Number of Neutral Results: {100 - positive_count - negative_count}")
    
        st.write(f"Overall Sentiment: {overall_sentiment}")
        
        st.subheader("10 Randomized Results:")
        
        random.shuffle(results_for_display)
        # Create a table for displaying randomized results
        table_data = []
        for result in results_for_display[:10]:
            table_data.append({'Title': result['title'], 'Description': result['description'], 'Sentiment': result['sentiment']})
        
        # Display the table with colored text for sentiment scores
        df = pd.DataFrame(table_data)
        st.table(df.style.applymap(lambda x: 'color: green' if x == 'Positive' else ('color: red' if x == 'Negative' else '')))