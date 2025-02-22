import pytest
import pandas as pd
import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from src.data.data_processor import DataProcessor
from src.utils.exceptions import DataProcessingError

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_reviews():
    return pd.DataFrame({
        'review_text': [
            "This product is very cheap but breaks easily.",
            "Excellent quality and worth every penny!",
            "Easy to use but a bit expensive."
        ],
        'rating': [2, 5, 4]
    })

def test_preprocess_text(data_processor):
    text = "This Product is GREAT!\n\nVery durable."
    processed = data_processor.preprocess_text(text)
    assert processed == "this product is great! very durable."

def test_calculate_aspect_scores(data_processor):
    text = "This product is cheap but breaks easily. Not worth the money."
    scores = data_processor.calculate_aspect_scores(text)
    
    # Check if all aspects are present
    assert all(aspect in scores for aspect in ['price', 'durability', 'quality'])
    
    # Price-related words should result in high price aspect score
    assert scores['price'] > 0

def test_filter_reviews_by_preference(data_processor, sample_reviews):
    # Process reviews
    processed_reviews, aspect_scores = data_processor.prepare_for_summarization(sample_reviews)
    
    # Test with high preference for price
    user_preferences = {
        'price': 1.0,
        'durability': 0.2,
        'ease_of_use': 0.2,
        'quality': 0.2,
        'performance': 0.2
    }
    
    filtered = data_processor.filter_reviews_by_preference(
        processed_reviews,
        aspect_scores,
        user_preferences
    )
    
    assert len(filtered) > 0
    # First review should contain price-related content
    assert any(word in filtered[0].lower() for word in ['cheap', 'expensive', 'price', 'cost'])

def test_invalid_data_handling(data_processor):
    with pytest.raises(DataProcessingError):
        data_processor.preprocess_text(None)

if __name__ == "__main__":
    pytest.main([__file__])
