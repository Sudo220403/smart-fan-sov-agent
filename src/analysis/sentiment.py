from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from nltk.sentiment import SentimentIntensityAnalyzer

@dataclass
class SentimentConfig:
    positive_threshold: float = 0.05
    negative_threshold: float = -0.05

class VaderSentiment:
    def __init__(self, cfg: SentimentConfig):
        self.cfg = cfg
        self.vader = SentimentIntensityAnalyzer()

    def label(self, text: str) -> dict:
        scores = self.vader.polarity_scores(text or "")
        comp = scores.get("compound", 0.0)
        if comp >= self.cfg.positive_threshold:
            label = "positive"
        elif comp <= self.cfg.negative_threshold:
            label = "negative"
        else:
            label = "neutral"
        scores["label"] = label
        return scores
