from __future__ import annotations
from dataclasses import dataclass
import pandas as pd
from collections import defaultdict
from typing import Iterable
from ..utils import engagement_weight, safe_div

@dataclass
class SovInputs:
    focal_brand: str
    brands: list[str]

def compute_sov(posts_df: pd.DataFrame, brands: list[str], focal_brand: str) -> pd.DataFrame:
    """Compute brand-level SOV using engagement-weighted mentions across posts."""
    # posts_df columns: ['post_id','platform','title','description','views','likes','comments','brand_hits']
    rows = []
    for _, row in posts_df.iterrows():
        w = engagement_weight(row.get("views"), row.get("likes"), row.get("comments"))
        hits: set[str] = row.get("brand_hits", set())
        for b in hits:
            rows.append({"brand": b, "weight": w, "post_id": row["post_id"]})
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["brand","weight","post_id"])
    totals = df.groupby("brand")["weight"].sum().rename("brand_weight")
    if totals.empty:
        return pd.DataFrame(columns=["brand","sov","brand_weight"])
    overall = totals.sum()
    out = totals.reset_index()
    out["sov"] = out["brand_weight"] / overall
    out = out.sort_values("sov", ascending=False).reset_index(drop=True)
    return out

def compute_spv(comment_df: pd.DataFrame, brands: list[str]) -> pd.DataFrame:
    """Compute Share of Positive Voice for each brand from labeled comments.
    comment_df columns: ['comment_id','brand','label'] with label in ['positive','neutral','negative']
    """
    if comment_df is None or comment_df.empty:
        return pd.DataFrame(columns=["brand","spv","pos","neg","neu","total"]).astype({"spv":"float"})
    grp = comment_df.groupby(["brand","label"]).size().unstack(fill_value=0)
    for col in ["positive","neutral","negative"]:
        if col not in grp.columns:
            grp[col] = 0
    grp["total"] = grp[["positive","neutral","negative"]].sum(axis=1)
    grp["spv"] = grp["positive"] / grp["total"].replace(0, pd.NA)
    grp = grp.reset_index()
    return grp[["brand","spv","positive","negative","neutral","total"]].rename(columns={"positive":"pos","negative":"neg","neutral":"neu"})
