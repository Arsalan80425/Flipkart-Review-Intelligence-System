# app.py

import streamlit as st
import pandas as pd
from scraper import scrape_flipkart_product
from nlp_utils import get_sentiment, summarize_review, generate_improvement_tip
from visualizer import plot_sentiment_distribution, plot_ratings_vs_sentiment, plot_wordcloud

st.set_page_config(page_title="Flipkart Product Review Dashboard", layout="wide")


st.title("📦 Flipkart Product Review Dashboard")
st.markdown("Analyze product reviews from Flipkart using NLP and visualizations.")

# Input Section
url = st.text_input("🔗 Enter Flipkart Product URL")

# Scrape + NLP
if st.button("Fetch Reviews"):
    if not url.strip():
        st.warning("Please enter a valid Flipkart product URL.")
    else:
        with st.spinner("⏳ Scraping and processing Flipkart data..."):
            product_info, reviews = scrape_flipkart_product(url)

            if not reviews:
                st.error("No reviews found or scraping failed.")
            else:
                # Process reviews
                for review in reviews:
                    review['sentiment'] = get_sentiment(review['content'])
                    # Using 'Summary' with a capital S
                    review['Summary'] = summarize_review(review['content'])
                    review['tip'] = generate_improvement_tip(review['sentiment'], review['content'])

                df = pd.DataFrame(reviews)

                # Store data in session
                st.session_state.product_info = product_info
                st.session_state.df = df
                st.rerun() # Rerun to enter the display block below smoothly

# Display Data
if 'df' in st.session_state and not st.session_state.df.empty:
    # Safely retrieve data from session_state
    df = st.session_state.df
    product_info = st.session_state.product_info

    # Product Info
    st.subheader("🛒 Product Details")
    st.markdown(f"**Title**: {product_info.get('title', 'N/A')}")
    st.markdown(f"**Price**: {product_info.get('price', 'N/A')}")
    st.markdown(f"**Rating**: {product_info.get('rating', 'N/A')} ⭐")
    st.markdown(f"**Total Ratings**: {product_info.get('total_ratings', 'N/A')}")
    st.markdown(f"**Total Reviews**: {product_info.get('total_reviews', 'N/A')}")

    st.divider()

    # Overall Summary Stats
    st.subheader("📈 Overall Review Sentiment Summary")
    total_reviews = len(df)
    positive_count = len(df[df['sentiment'] == 'Positive'])
    neutral_count = len(df[df['sentiment'] == 'Neutral'])
    negative_count = len(df[df['sentiment'] == 'Negative'])

    # Calculate percentages
    positive_pct = round((positive_count / total_reviews) * 100, 2) if total_reviews > 0 else 0
    neutral_pct = round((neutral_count / total_reviews) * 100, 2) if total_reviews > 0 else 0
    negative_pct = round((negative_count / total_reviews) * 100, 2) if total_reviews > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reviews", total_reviews)
    col2.metric("🟢 Positive", f"{positive_pct}%", delta=positive_count)
    col3.metric("⚪ Neutral", f"{neutral_pct}%", delta=neutral_count)
    col4.metric("🔴 Negative", f"{negative_pct}%", delta=negative_count)

    st.divider()

    # Charts
    st.subheader("📊 Review Analytics")
    col1, col2 = st.columns(2)
    with col1:
        plot_sentiment_distribution(df)
    with col2:
        plot_ratings_vs_sentiment(df)

    if st.checkbox("🎨 Show WordCloud of Reviews"):
        plot_wordcloud(df)

    st.divider()

    # Filters
    st.subheader("🔍 Filter Reviews")
    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        sentiment_filter = st.multiselect(
            "Filter by Sentiment",
            options=["Positive", "Neutral", "Negative"],
            default=["Positive", "Neutral", "Negative"]
        )

    with filter_col2:
        if 'rating' in df.columns:
            rating_options = sorted(df['rating'].unique())
            rating_filter = st.multiselect(
                "Filter by Rating (stars)",
                options=rating_options,
                default=rating_options
            )
        else:
            rating_filter = []


    # Apply filters
    filtered_df = df.copy() # Starting with a copy to avoid chained assignment warnings
    if 'sentiment' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['sentiment'].isin(sentiment_filter)]
    if 'rating' in filtered_df.columns and rating_filter:
        filtered_df = filtered_df[filtered_df['rating'].isin(rating_filter)]

    # Review Table
    st.subheader("📋 Processed Reviews")
    display_cols = ['rating', 'sentiment', 'Summary', 'tip']
    cols_to_show = [col for col in display_cols if col in filtered_df.columns]
    st.dataframe(filtered_df[cols_to_show], use_container_width=True)

    st.markdown(
        "<div style='font-size: 0.9em; color: gray;'>📌 Double-click on a cell to fully view the content if it's truncated.</div>",
        unsafe_allow_html=True
    )

else:
    st.info("Please enter a Flipkart URL and click 'Fetch Reviews' to begin.")