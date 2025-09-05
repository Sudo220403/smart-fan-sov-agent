import re
import math
from typing import Iterable

def normalize_text(s: str) -> str:
    return (s or "").lower()

def tokenize(s: str) -> list[str]:
    return re.findall(r"[a-z0-9\-\+]+", normalize_text(s))

def safe_div(a: float, b: float) -> float:
    return a / b if b else 0.0

def engagement_weight(views: int|None, likes: int|None, comments: int|None) -> float:
    # Simple monotonic weight: log(1+views) + 2*log(1+likes) + 3*log(1+comments)
    v = math.log1p(views or 0)
    l = 2 * math.log1p(likes or 0)
    c = 3 * math.log1p(comments or 0)
    return v + l + c

def any_mention(text: str, brands: Iterable[str]) -> set[str]:
    text_l = normalize_text(text)
    hits = set()
    for b in brands:
        if b in text_l:
            hits.add(b)
    return hits
