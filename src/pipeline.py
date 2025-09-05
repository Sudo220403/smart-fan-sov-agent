from __future__ import annotations
import json, os, datetime as dt
import pandas as pd
from typing import Iterable, List, Dict, Any, Set
from .config import AppConfig
from .platforms.youtube_client import YouTubeClient
from .brand_matching import mentions_in_text
from .analysis.sentiment import VaderSentiment, SentimentConfig
from .analysis.metrics import compute_sov, compute_spv
from .utils import any_mention

class SovPipeline:
    def __init__(self, cfg: AppConfig, out_dir: str = "reports"):
        self.cfg = cfg
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        os.makedirs(os.path.join(self.out_dir, "exports"), exist_ok=True)
        self.yt = YouTubeClient(api_key=self.cfg.youtube_api_key)
        self.sent = VaderSentiment(SentimentConfig(self.cfg.positive_threshold, self.cfg.negative_threshold))

    def run(self, keywords: list[str], top_n: int = 30, days: int = 365) -> dict:
        run_time = dt.datetime.utcnow().isoformat()
        published_after = (dt.datetime.utcnow() - dt.timedelta(days=days)).isoformat("T") + "Z"

        posts_rows = []
        comments_rows = []

        for kw in keywords:
            search_items = self.yt.search(kw, max_results=top_n, published_after=published_after)
            video_ids = [it["id"]["videoId"] for it in search_items if it.get("id",{}).get("videoId")]
            stats = self.yt.videos_stats(video_ids)

            for vid in video_ids:
                meta = stats.get(vid, {})
                title = meta.get("title","");
                desc = meta.get("description","");
                brand_hits = mentions_in_text(title + "\n" + desc, self.cfg.brand_list)

                posts_rows.append({
                    "keyword": kw,
                    "platform": "youtube",
                    "post_id": vid,
                    "title": title,
                    "description": desc,
                    "channel": meta.get("channelTitle",""),
                    "publishedAt": meta.get("publishedAt",""),
                    "views": meta.get("views",0),
                    "likes": meta.get("likes",0),
                    "comments": meta.get("comments",0),
                    "brand_hits": brand_hits,
                })

                if self.cfg.max_comments_per_video > 0:
                    comms = self.yt.fetch_comments(vid, max_comments=self.cfg.max_comments_per_video)
                    for c in comms:
                        # brand tagging at comment-level (may include multiple)
                        hits = mentions_in_text(c.get("text",""), self.cfg.brand_list)
                        if not hits:
                            continue
                        label_scores = self.sent.label(c.get("text",""))
                        for b in hits:
                            comments_rows.append({
                                "post_id": vid,
                                "comment_id": c.get("comment_id"),
                                "brand": b,
                                "text": c.get("text",""),
                                "label": label_scores["label"],
                                "compound": label_scores["compound"],
                                "pos": label_scores.get("pos",0.0),
                                "neg": label_scores.get("neg",0.0),
                                "neu": label_scores.get("neu",0.0),
                            })

        posts_df = pd.DataFrame(posts_rows)
        comments_df = pd.DataFrame(comments_rows)

        sov_df = compute_sov(posts_df, list(self.cfg.brand_list), self.cfg.focal_brand)
        spv_df = compute_spv(comments_df, list(self.cfg.brand_list))

        # exports
        exports_dir = os.path.join(self.out_dir, "exports")
        posts_path = os.path.join(exports_dir, "posts.csv")
        comments_path = os.path.join(exports_dir, "brand_comments.csv")
        sov_path = os.path.join(exports_dir, "sov.csv")
        spv_path = os.path.join(exports_dir, "spv.csv")

        posts_df.to_csv(posts_path, index=False)
        comments_df.to_csv(comments_path, index=False)
        sov_df.to_csv(sov_path, index=False)
        spv_df.to_csv(spv_path, index=False)

        run_cfg = {
            "run_time": run_time,
            "params": {"top_n": top_n, "days": days},
            "keywords": keywords,
            "exports": {"posts": posts_path, "comments": comments_path, "sov": sov_path, "spv": spv_path},
        }
        with open(os.path.join(self.out_dir, "run_config.json"), "w", encoding="utf-8") as f:
            json.dump(run_cfg, f, indent=2)

        # basic insights (text)
        insights = self._compose_insights(sov_df, spv_df)
        with open(os.path.join(self.out_dir, "insights.md"), "w", encoding="utf-8") as f:
            f.write(insights)

        return run_cfg

    def _compose_insights(self, sov_df, spv_df) -> str:
        lines = ["# Insights (Auto-Generated)"]
        if sov_df is None or sov_df.empty:
            lines.append("No brand mentions detected in the selected corpus. Consider increasing Top-N or keywords.")
            return "\n".join(lines)
        top = sov_df.head(5).copy()
        lines.append("\n## Top Brands by SoV")
        lines.append(top.to_markdown(index=False))
        if spv_df is not None and not spv_df.empty:
            lines.append("\n## Share of Positive Voice (SPV)")
            lines.append(spv_df.sort_values("spv", ascending=False).to_markdown(index=False))
        lines.append("\n*Tip:* Try more keywords like 'BLDC fan', 'voice control fan', 'IoT fan'.")
        return "\n".join(lines)
