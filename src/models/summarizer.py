import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from typing import List, Optional
from ..utils.logger import app_logger
from ..utils.exceptions import ModelError
from ..config.config import config

class ReviewSummarizer:
    def __init__(self):
        """Initialize the T5 model and tokenizer."""
        try:
            # Determine the best available device
            if torch.cuda.is_available():
                self.device = torch.device("cuda")
                app_logger.info("Using CUDA for GPU acceleration")
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = torch.device("mps")
                app_logger.info("Using MPS (Metal Performance Shaders) for M1 Mac acceleration")
            else:
                self.device = torch.device("cpu")
                app_logger.info("Using CPU for computation")

            # Load model and tokenizer with error handling
            try:
                self.model_name = config.model.model_name
                self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
                self.model = T5ForConditionalGeneration.from_pretrained(self.model_name)
                self.model.to(self.device)
                app_logger.info(f"Successfully loaded {self.model_name} model")
            except Exception as model_error:
                app_logger.error(f"Error loading model or tokenizer: {str(model_error)}")
                raise ModelError("Failed to load model or tokenizer", error=model_error)
            
        except Exception as e:
            app_logger.error(f"Error initializing model: {str(e)}")
            raise ModelError("Failed to initialize model", error=e)

    def _prepare_input_text(self, reviews: List[str]) -> str:
        """
        Prepare reviews for input to T5 model.
        
        Args:
            reviews (List[str]): List of preprocessed reviews
            
        Returns:
            str: Concatenated reviews with prefix
        """
        try:
            # Concatenate reviews with separator
            combined_reviews = " [REVIEW] ".join(reviews)
            # Add summarization prefix
            input_text = f"summarize: {combined_reviews}"
            
            return input_text
            
        except Exception as e:
            app_logger.error(f"Error preparing input text: {str(e)}")
            raise ModelError("Failed to prepare input text", error=e)

    def _chunk_text(self, text: str, max_length: int) -> List[str]:
        """
        Split text into chunks that fit within model's max length.
        
        Args:
            text (str): Input text to chunk
            max_length (int): Maximum token length
            
        Returns:
            List[str]: List of text chunks
        """
        try:
            # Tokenize text
            tokens = self.tokenizer.encode(text)
            chunks = []
            
            # Split into chunks
            current_chunk = []
            current_length = 0
            
            for token in tokens:
                if current_length + 1 > max_length:
                    chunks.append(self.tokenizer.decode(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(token)
                current_length += 1
            
            if current_chunk:
                chunks.append(self.tokenizer.decode(current_chunk))
            
            return chunks
            
        except Exception as e:
            app_logger.error(f"Error chunking text: {str(e)}")
            raise ModelError("Failed to chunk text", error=e)

    def generate_summary(self, reviews: List[str]) -> str:
        """
        Generate summary from reviews using T5 model.
        
        Args:
            reviews (List[str]): List of preprocessed reviews
            
        Returns:
            str: Generated summary
        """
        try:
            input_text = self._prepare_input_text(reviews)
            chunks = self._chunk_text(input_text, config.model.max_length)
            summaries = []
            
            for chunk in chunks:
                # Tokenize input
                inputs = self.tokenizer(
                    chunk,
                    max_length=config.model.max_length,
                    truncation=True,
                    padding=True,
                    return_tensors="pt"
                )
                inputs = inputs.to(self.device)
                
                # Generate summary
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs["input_ids"],
                        max_length=config.model.max_length,
                        min_length=config.model.min_length,
                        num_beams=config.model.num_beams,
                        early_stopping=True
                    )
                
                # Decode summary
                summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                summaries.append(summary)
            
            # Combine chunk summaries
            final_summary = " ".join(summaries)
            app_logger.info("Successfully generated summary")
            
            return final_summary
            
        except Exception as e:
            app_logger.error(f"Error generating summary: {str(e)}")
            raise ModelError("Failed to generate summary", error=e)

    def personalize_summary(self, summary: str, user_preferences: dict) -> str:
        """
        Adjust the summary based on user preferences.
        
        Args:
            summary (str): Generated summary
            user_preferences (dict): User's aspect preferences
            
        Returns:
            str: Personalized summary
        """
        try:
            # Split summary into sentences
            sentences = summary.split('. ')
            
            # Score each sentence based on aspects
            sentence_scores = []
            for sentence in sentences:
                score = 0
                for aspect, weight in user_preferences.items():
                    keywords = config.aspects.aspect_keywords[aspect]
                    # Calculate aspect relevance
                    relevance = sum(1 for keyword in keywords if keyword in sentence.lower())
                    score += relevance * weight
                sentence_scores.append(score)
            
            # Sort sentences by relevance score
            sorted_pairs = sorted(zip(sentences, sentence_scores), key=lambda x: x[1], reverse=True)
            
            # Reconstruct summary with most relevant sentences first
            personalized_summary = '. '.join(sentence for sentence, _ in sorted_pairs)
            if not personalized_summary.endswith('.'):
                personalized_summary += '.'
                
            app_logger.info("Successfully personalized summary")
            return personalized_summary
            
        except Exception as e:
            app_logger.error(f"Error personalizing summary: {str(e)}")
            raise ModelError("Failed to personalize summary", error=e)
