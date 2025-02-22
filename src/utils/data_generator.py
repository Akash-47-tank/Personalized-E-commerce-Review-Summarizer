import random
import pandas as pd
from typing import List, Dict
import os

class ReviewGenerator:
    def __init__(self):
        # Templates for different aspects
        self.price_templates = [
            "The price is {price_adj}, but {value_prop}.",
            "At {price_amount}, this product is {price_value}.",
            "{price_value} considering the features you get.",
            "The price point is {price_adj} for what you get.",
            "It's {price_adj} compared to similar products."
        ]
        
        self.durability_templates = [
            "The build quality is {durability_adj}. {durability_detail}",
            "{durability_time} of use and {durability_condition}.",
            "In terms of durability, {durability_opinion}.",
            "{durability_event} and {durability_result}.",
            "The material quality is {durability_adj}."
        ]
        
        self.ease_of_use_templates = [
            "The interface is {usability_adj}. {usage_detail}",
            "Setting it up was {setup_exp}. {setup_detail}",
            "{user_type} would find it {usability_adj} to use.",
            "The learning curve is {learning_curve}. {learning_detail}",
            "Navigation is {navigation_exp}."
        ]
        
        self.quality_templates = [
            "The overall quality is {quality_adj}. {quality_detail}",
            "Quality-wise, {quality_opinion}.",
            "The {component} quality is {quality_adj}.",
            "{quality_time} and {quality_condition}.",
            "For the quality you get, {quality_value}."
        ]
        
        self.performance_templates = [
            "Performance is {performance_adj}. {performance_detail}",
            "It handles {task} {performance_adv}.",
            "In terms of speed, {speed_opinion}.",
            "{performance_scenario} with {performance_result}.",
            "The {performance_aspect} is {performance_adj}."
        ]

        # Adjectives and phrases for each aspect
        self.price_data = {
            'price_adj': ['expensive', 'reasonable', 'premium', 'budget-friendly', 'overpriced', 'affordable', 'steep', 'competitive'],
            'price_amount': ['$999', '$799', '$1299', '$599', '$1499', '$899'],
            'price_value': ['worth every penny', 'a bit overpriced', 'great value for money', 'reasonably priced', 'on the expensive side'],
            'value_prop': ['the quality justifies it', 'you get what you pay for', 'could be more competitive', 'it offers good value', 'the features make up for it']
        }
        
        self.durability_data = {
            'durability_adj': ['excellent', 'solid', 'questionable', 'impressive', 'poor', 'outstanding'],
            'durability_time': ['After six months', 'Two years', 'Three months', 'One year', 'Just a few weeks'],
            'durability_condition': ['still looks brand new', 'showing signs of wear', 'working perfectly', 'no issues at all', 'needs replacement'],
            'durability_opinion': ['it feels very sturdy', 'it seems fragile', "it's built to last", 'durability is concerning', "it's rock solid"],
            'durability_event': ['Dropped it several times', 'Used it daily', 'Traveled with it', 'Exposed to elements'],
            'durability_result': ['no scratches at all', 'minor wear visible', 'still perfect', 'some damage occurred', 'held up well']
        }
        
        self.ease_of_use_data = {
            'usability_adj': ['intuitive', 'straightforward', 'complicated', 'user-friendly', 'confusing'],
            'usage_detail': ['Everything is where you expect it', 'Takes time to get used to', 'Very well designed', 'Could be more intuitive'],
            'setup_exp': ['a breeze', 'straightforward', 'time-consuming', 'simple', 'complicated'],
            'setup_detail': ['No manual needed', 'Required some help', 'Instructions were clear', 'Could be simpler'],
            'user_type': ['Beginners', 'Tech-savvy users', 'Everyone', 'Most people', 'Experts'],
            'learning_curve': ['gentle', 'steep', 'moderate', 'minimal', 'significant'],
            'learning_detail': ['You\'ll get the hang of it quickly', 'Takes time to master', 'Pretty straightforward to learn'],
            'navigation_exp': ['smooth and intuitive', 'a bit confusing', 'well-designed', 'could be better', 'excellent']
        }
        
        self.quality_data = {
            'quality_adj': ['exceptional', 'superior', 'average', 'disappointing', 'outstanding'],
            'quality_detail': ['Attention to detail is evident', 'Some flaws are visible', 'Meets expectations', 'Exceeds expectations'],
            'quality_opinion': ['it exceeds expectations', 'there\'s room for improvement', 'it\'s top-notch', 'it\'s satisfactory'],
            'component': ['build', 'material', 'finish', 'design', 'craftsmanship'],
            'quality_time': ['After extensive use', 'From day one', 'Over time', 'With regular use'],
            'quality_condition': ['quality remains consistent', 'shows no degradation', 'maintains its premium feel', 'quality is evident'],
            'quality_value': ['it\'s a premium product', 'it meets expectations', 'it\'s worth the investment', 'it\'s satisfactory']
        }
        
        self.performance_data = {
            'performance_adj': ['excellent', 'impressive', 'inconsistent', 'stellar', 'mediocre'],
            'performance_detail': ['No lag or slowdown', 'Some occasional hiccups', 'Runs smoothly', 'Could be faster'],
            'task': ['heavy workloads', 'multiple tasks', 'intensive applications', 'basic operations', 'demanding software'],
            'performance_adv': ['effortlessly', 'with some struggle', 'smoothly', 'adequately', 'impressively'],
            'speed_opinion': ['it\'s lightning fast', 'it could be faster', 'it\'s consistently quick', 'it\'s satisfactory'],
            'performance_scenario': ['Under heavy load', 'During normal use', 'In demanding situations', 'For everyday tasks'],
            'performance_result': ['excellent results', 'some slowdown', 'consistent performance', 'impressive speed'],
            'performance_aspect': ['response time', 'processing speed', 'overall performance', 'system efficiency']
        }

    def _format_template(self, template: str, data: Dict[str, List[str]]) -> str:
        """Format a template with random selections from data."""
        result = template
        for key, values in data.items():
            if '{' + key + '}' in template:
                result = result.replace('{' + key + '}', random.choice(values))
        return result

    def generate_review(self) -> tuple:
        """Generate a single review with rating."""
        aspects = ['price', 'durability', 'ease_of_use', 'quality', 'performance']
        
        # Select 2-4 aspects to focus on
        selected_aspects = random.sample(aspects, random.randint(2, 4))
        review_parts = []
        
        for aspect in selected_aspects:
            if aspect == 'price':
                review_parts.append(self._format_template(random.choice(self.price_templates), self.price_data))
            elif aspect == 'durability':
                review_parts.append(self._format_template(random.choice(self.durability_templates), self.durability_data))
            elif aspect == 'ease_of_use':
                review_parts.append(self._format_template(random.choice(self.ease_of_use_templates), self.ease_of_use_data))
            elif aspect == 'quality':
                review_parts.append(self._format_template(random.choice(self.quality_templates), self.quality_data))
            elif aspect == 'performance':
                review_parts.append(self._format_template(random.choice(self.performance_templates), self.performance_data))
        
        # Combine parts into a full review
        review = ' '.join(review_parts)
        
        # Generate rating based on sentiment words in the review
        positive_words = ['excellent', 'impressive', 'worth', 'great', 'perfect', 'outstanding']
        negative_words = ['poor', 'disappointing', 'overpriced', 'complicated', 'confusing']
        
        review_lower = review.lower()
        positive_count = sum(1 for word in positive_words if word in review_lower)
        negative_count = sum(1 for word in negative_words if word in review_lower)
        
        # Calculate rating based on sentiment
        if positive_count > negative_count:
            rating = random.randint(4, 5)
        elif positive_count < negative_count:
            rating = random.randint(1, 3)
        else:
            rating = random.randint(3, 4)
        
        return review, rating

    def generate_dataset(self, num_reviews: int = 200) -> pd.DataFrame:
        """Generate a dataset with specified number of reviews."""
        reviews = []
        ratings = []
        
        for _ in range(num_reviews):
            review, rating = self.generate_review()
            reviews.append(review)
            ratings.append(rating)
        
        return pd.DataFrame({
            'review_text': reviews,
            'rating': ratings
        })

def generate_sample_data(output_path: str, num_reviews: int = 200):
    """Generate sample review data and save to CSV."""
    generator = ReviewGenerator()
    df = generator.generate_dataset(num_reviews)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_reviews} reviews and saved to {output_path}")

if __name__ == "__main__":
    # Generate sample data
    output_path = "data/generated_reviews.csv"
    generate_sample_data(output_path)
