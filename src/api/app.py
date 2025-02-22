import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
import torch

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path.parent))

from src.data.data_processor import DataProcessor
from src.models.summarizer import ReviewSummarizer
from src.utils.logger import app_logger
from src.config.config import config
from src.utils.exceptions import ReviewSummarizerException

# Disable watchdog to prevent torch-streamlit conflicts
import streamlit.runtime.scriptrunner.script_runner
streamlit.runtime.scriptrunner.script_runner.RerunException = Exception

# Initialize processors outside of Streamlit's caching mechanism
try:
    data_processor = DataProcessor()
    app_logger.info("DataProcessor initialized successfully")
except Exception as e:
    app_logger.error(f"Error initializing DataProcessor: {str(e)}")
    data_processor = None

try:
    summarizer = ReviewSummarizer()
    app_logger.info("ReviewSummarizer initialized successfully")
except Exception as e:
    app_logger.error(f"Error initializing ReviewSummarizer: {str(e)}")
    summarizer = None

def check_initialization():
    """Check if all components are properly initialized."""
    if data_processor is None:
        st.error("Error: Data processor failed to initialize. Please check the logs.")
        return False
    if summarizer is None:
        st.error("Error: Summarizer failed to initialize. Please check the logs.")
        return False
    return True

def main():
    try:
        # Page config
        st.set_page_config(
            page_title="Product Review Summarizer",
            page_icon="📝",
            layout="wide"
        )

        # Title and description
        st.title("Personalized E-commerce Product Review Summarizer")
        st.markdown("""
        Upload your product reviews and get personalized summaries based on what matters most to you.
        Optimized for performance on M1 Mac!
        """)

        # Check initialization
        if not check_initialization():
            return

        # File upload
        uploaded_file = st.file_uploader(
            "Upload your reviews CSV file (must contain 'review_text' and 'rating' columns)",
            type=['csv']
        )

        if uploaded_file:
            try:
                # Save uploaded file temporarily
                temp_path = os.path.join(config.data_path, "temp_reviews.csv")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Load and process data
                df = data_processor.load_data(temp_path)
                st.success(f"Successfully loaded {len(df)} reviews!")

                # Display sample of reviews
                with st.expander("View sample reviews"):
                    st.dataframe(df[['review_text', 'rating']].head())

                # Aspect preference sliders
                st.subheader("Customize Your Summary")
                st.markdown("Adjust the importance of each aspect (0 = not important, 1 = very important)")

                col1, col2 = st.columns(2)
                user_preferences = {}

                with col1:
                    for aspect in config.aspects.aspects[:3]:
                        user_preferences[aspect] = st.slider(
                            f"{aspect.replace('_', ' ').title()}",
                            0.0, 1.0, 0.5,
                            key=aspect
                        )

                with col2:
                    for aspect in config.aspects.aspects[3:]:
                        user_preferences[aspect] = st.slider(
                            f"{aspect.replace('_', ' ').title()}",
                            0.0, 1.0, 0.5,
                            key=aspect
                        )

                if st.button("Generate Summary"):
                    with st.spinner("Processing reviews..."):
                        # Prepare reviews
                        processed_reviews, aspect_scores = data_processor.prepare_for_summarization(df)
                        
                        # Filter reviews based on preferences
                        filtered_reviews = data_processor.filter_reviews_by_preference(
                            processed_reviews,
                            aspect_scores,
                            user_preferences
                        )
                        
                        # Generate base summary
                        base_summary = summarizer.generate_summary(filtered_reviews)
                        
                        # Personalize summary
                        final_summary = summarizer.personalize_summary(
                            base_summary,
                            user_preferences
                        )
                        
                        # Display results
                        st.subheader("Personalized Summary")
                        st.write(final_summary)
                        
                        # Display aspect coverage
                        st.subheader("Aspect Coverage in Summary")
                        coverage = {}
                        for aspect in config.aspects.aspects:
                            keywords = config.aspects.aspect_keywords[aspect]
                            coverage[aspect] = sum(1 for keyword in keywords if keyword in final_summary.lower())
                        
                        # Create coverage chart
                        coverage_df = pd.DataFrame({
                            'Aspect': list(coverage.keys()),
                            'Coverage': list(coverage.values())
                        })
                        st.bar_chart(coverage_df.set_index('Aspect'))

            except Exception as e:
                st.error(f"Error processing reviews: {str(e)}")
                app_logger.error(f"Error in main app: {str(e)}")

    except Exception as e:
        st.error("An unexpected error occurred. Please try again.")
        app_logger.error(f"Critical error in main app: {str(e)}")

if __name__ == "__main__":
    main()
