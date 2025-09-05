import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppConfig:
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    # Tunables
    max_results: int = 30
    max_comments_per_video: int = 200
    positive_threshold: float = 0.05  # VADER compound > this -> positive
    negative_threshold: float = -0.05 # VADER compound < this -> negative
    brand_list: tuple = (
        "atomberg",
        "havells",
        "crompton",
        "usha",
        "orient electric",
        "bajaj",
        "panasonic",
        "polycab",
        "lg",
        "philips",
        "superfan",
        "v-guard",
    )
    # core brand (focus)
    focal_brand: str = "atomberg"
