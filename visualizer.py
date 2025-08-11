import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import streamlit as st

# Pie Chart: Sentiment Distribution
def plot_sentiment_distribution(df: pd.DataFrame):
    fig = px.pie(
        df,
        names='sentiment',
        title="Sentiment Distribution of Reviews",
        color='sentiment',
        color_discrete_map={
            "Positive": "#84f97eeb",  
            "Neutral": "#689efa",   
            "Negative": "#fa6f6fff"   
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# Bar Chart: Star Ratings vs Sentiment
def plot_ratings_vs_sentiment(df: pd.DataFrame):
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    grouped = df.groupby(['rating', 'sentiment']).size().reset_index(name='count')

    fig = px.bar(
        grouped,
        x='rating',
        y='count',
        color='sentiment',
        title="Star Ratings vs Sentiment",
        barmode='group',
        color_discrete_map={
            "Positive": "#6df965",
            "Neutral": "#689efa",
            "Negative": "#fc5555"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Optional WordCloud
def plot_wordcloud(df: pd.DataFrame):
    text = " ".join(df['content'].dropna().astype(str).tolist())
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=200
    ).generate(text)

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)
