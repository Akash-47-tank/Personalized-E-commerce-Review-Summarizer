import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from ..utils.logger import app_logger
from ..utils.exceptions import DataProcessingError
from ..config.config import config
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import os
import ssl

class DataProcessor:
    def __init__(self):
        """Initialize the DataProcessor with necessary NLTK downloads."""
        try:
            # Create NLTK data directory if it doesn't exist
            nltk_data_dir = os.path.expanduser('~/nltk_data')
            if not os.path.exists(nltk_data_dir):
                os.makedirs(nltk_data_dir)
            
            # Handle SSL certificate issues for NLTK downloads
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context

            # Download required NLTK data with error handling
            for resource in ['punkt', 'stopwords']:
                try:
                    nltk.data.find(f'tokenizers/{resource}')
                except LookupError:
                    app_logger.info(f"Downloading NLTK resource: {resource}")
                    nltk.download(resource, quiet=True)

            # Initialize stopwords
            self.stop_words = set(stopwords.words('english'))
            app_logger.info("DataProcessor initialized successfully with NLTK resources")
            
        except Exception as e:
            app_logger.error(f"Error initializing DataProcessor: {str(e)}")
            raise DataProcessingError("Failed to initialize DataProcessor", error=e)

    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load review data from CSV file.
        
        Args:
            file_path (str): Path to the CSV file containing reviews
            
        Returns:
            pd.DataFrame: Loaded and preprocessed review data
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
                
            df = pd.read_csv(file_path)
            required_columns = ['review_text', 'rating']
            
            # Validate required columns
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV must contain columns: {required_columns}")
                
            # Basic preprocessing
            df = df.dropna(subset=['review_text'])
            df = df.head(config.data.max_reviews)  # Limit number of reviews
            
            app_logger.info(f"Successfully loaded {len(df)} reviews from {file_path}")
            return df
            
        except Exception as e:
            app_logger.error(f"Error loading data: {str(e)}")
            raise DataProcessingError("Failed to load review data", error=e)

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess review text.
        
        Args:
            text (str): Raw review text
            
        Returns:
            str: Preprocessed text
        """
        try:
            # Convert to lowercase
            text = text.lower()
            
            # Basic cleaning
            text = text.replace('\n', ' ').replace('\r', ' ')
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            return text
            
        except Exception as e:
            app_logger.error(f"Error preprocessing text: {str(e)}")
            raise DataProcessingError("Failed to preprocess text", error=e)

    def calculate_aspect_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate aspect scores for a given review text.
        
        Args:
            text (str): Preprocessed review text
            
        Returns:
            Dict[str, float]: Dictionary of aspect scores
        """
        try:
            text = self.preprocess_text(text)
            
            try:
                words = word_tokenize(text)
            except LookupError:
                # Fallback to basic tokenization if NLTK fails
                words = text.split()
            
            words = [w for w in words if w not in self.stop_words]
            
            scores = {}
            for aspect, keywords in config.aspects.aspect_keywords.items():
                # Count occurrences of aspect keywords
                keyword_count = sum(1 for word in words if word in keywords)
                # Normalize score between 0 and 1
                scores[aspect] = min(1.0, keyword_count / len(words) * 5)
            
            return scores
            
        except Exception as e:
            app_logger.error(f"Error calculating aspect scores: {str(e)}")
            raise DataProcessingError("Failed to calculate aspect scores", error=e)

    def prepare_for_summarization(self, reviews: pd.DataFrame) -> Tuple[List[str], List[Dict[str, float]]]:
        """
        Prepare reviews for summarization.
        
        Args:
            reviews (pd.DataFrame): DataFrame containing reviews
            
        Returns:
            Tuple[List[str], List[Dict[str, float]]]: Preprocessed reviews and their aspect scores
        """
        try:
            processed_reviews = []
            aspect_scores_list = []
            
            for _, row in reviews.iterrows():
                processed_text = self.preprocess_text(row['review_text'])
                aspect_scores = self.calculate_aspect_scores(processed_text)
                
                processed_reviews.append(processed_text)
                aspect_scores_list.append(aspect_scores)
            
            app_logger.info(f"Successfully prepared {len(processed_reviews)} reviews for summarization")
            return processed_reviews, aspect_scores_list
            
        except Exception as e:
            app_logger.error(f"Error preparing reviews for summarization: {str(e)}")
            raise DataProcessingError("Failed to prepare reviews for summarization", error=e)

    def filter_reviews_by_preference(
        self,
        reviews: List[str],
        aspect_scores: List[Dict[str, float]],
        user_preferences: Dict[str, float]
    ) -> List[str]:
        """
        Filter and prioritize reviews based on user preferences.
        
        Args:
            reviews (List[str]): List of preprocessed reviews
            aspect_scores (List[Dict[str, float]]): List of aspect scores for each review
            user_preferences (Dict[str, float]): User's aspect preferences
            
        Returns:
            List[str]: Filtered and prioritized reviews
        """
        try:
            # Calculate relevance score for each review
            relevance_scores = []
            for review_scores in aspect_scores:
                score = sum(
                    review_scores[aspect] * pref_score
                    for aspect, pref_score in user_preferences.items()
                )
                relevance_scores.append(score)
            
            # Sort reviews by relevance
            sorted_indices = np.argsort(relevance_scores)[::-1]
            filtered_reviews = [reviews[i] for i in sorted_indices[:config.data.max_reviews]]
            
            app_logger.info(f"Successfully filtered reviews based on user preferences")
            return filtered_reviews
            
        except Exception as e:
            app_logger.error(f"Error filtering reviews by preference: {str(e)}")
            raise DataProcessingError("Failed to filter reviews by preference", error=e)
