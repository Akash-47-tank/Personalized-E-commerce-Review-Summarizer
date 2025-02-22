class ReviewSummarizerException(Exception):
    """Base exception class for the Review Summarizer project."""
    def __init__(self, message: str = None, error: Exception = None):
        self.message = message
        self.error = error
        super().__init__(self.message)

class DataProcessingError(ReviewSummarizerException):
    """Raised when there's an error processing the review data."""
    pass

class ModelError(ReviewSummarizerException):
    """Raised when there's an error with the model operations."""
    pass

class ConfigError(ReviewSummarizerException):
    """Raised when there's an error in configuration."""
    pass

class ValidationError(ReviewSummarizerException):
    """Raised when there's an error in input validation."""
    pass
