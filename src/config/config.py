import os
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ModelConfig:
    model_name: str = "t5-small"  # Using t5-small for M1 Mac optimization
    max_length: int = 512
    min_length: int = 50
    num_beams: int = 4
    device: str = "mps"  # Metal Performance Shaders for M1 Mac
    batch_size: int = 8

@dataclass
class AspectConfig:
    aspects: List[str] = field(default_factory=lambda: [
        "price",
        "durability",
        "ease_of_use",
        "quality",
        "performance"
    ])
    
    aspect_keywords: Dict[str, List[str]] = field(default_factory=lambda: {
        "price": ["price", "cost", "expensive", "cheap", "affordable", "value", "worth"],
        "durability": ["durable", "sturdy", "break", "broken", "last", "quality", "build"],
        "ease_of_use": ["easy", "simple", "complicated", "difficult", "user-friendly", "intuitive"],
        "quality": ["quality", "excellent", "poor", "great", "bad", "premium", "superior"],
        "performance": ["performance", "fast", "slow", "efficient", "powerful", "weak"]
    })

@dataclass
class DataConfig:
    data_dir: str = "data"
    max_reviews: int = 200
    train_size: float = 0.8
    random_seed: int = 42

@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    aspects: AspectConfig = field(default_factory=AspectConfig)
    data: DataConfig = field(default_factory=DataConfig)
    base_path: str = field(init=False)
    model_path: str = field(init=False)
    data_path: str = field(init=False)
    log_path: str = field(init=False)
    
    def __post_init__(self):
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.model_path = os.path.join(self.base_path, "models")
        self.data_path = os.path.join(self.base_path, "data")
        self.log_path = os.path.join(self.base_path, "logs")
        
        # Create directories if they don't exist
        for path in [self.model_path, self.data_path, self.log_path]:
            if not os.path.exists(path):
                os.makedirs(path)

# Create global config instance
config = Config()
