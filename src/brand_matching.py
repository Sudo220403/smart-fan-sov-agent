from __future__ import annotations
from typing import Iterable, Set
from .utils import normalize_text

def mentions_in_text(text: str, brands: Iterable[str]) -> Set[str]:
    t = normalize_text(text)
    hits = set()
    for b in brands:
        if b in t:
            hits.add(b)
    return hits
