from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from googleapiclient.discovery import build


@dataclass
class YouTubeClient:
    api_key: str

    def _svc(self):
        return build("youtube", "v3", developerKey=self.api_key, cache_discovery=False)

    def search(self, query: str, max_results: int = 25, published_after: str | None = None) -> List[Dict[str, Any]]:
        svc = self._svc()
        try:
            req = svc.search().list(
                part="id,snippet",
                q=query,
                type="video",
                maxResults=min(max_results, 50),
                order="relevance",
                publishedAfter=published_after
            )
            resp = req.execute()
            return resp.get("items", [])
        except Exception as e:
            print(f"[WARN] YouTube search failed for '{query}': {e}")
            return []

    def videos_stats(self, video_ids: list[str]) -> Dict[str, dict]:
        if not video_ids:
            return {}
        svc = self._svc()
        out = {}
        try:
            req = svc.videos().list(part="statistics,snippet", id=",".join(video_ids))
            resp = req.execute()
            for it in resp.get("items", []):
                vid = it["id"]
                stats = it.get("statistics", {})
                snip = it.get("snippet", {})
                out[vid] = {
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)) if stats.get("likeCount") is not None else 0,
                    "comments": int(stats.get("commentCount", 0)),
                    "title": snip.get("title", ""),
                    "description": snip.get("description", ""),
                    "channelTitle": snip.get("channelTitle", ""),
                    "publishedAt": snip.get("publishedAt", ""),
                }
        except Exception as e:
            print(f"[WARN] Failed to fetch video stats: {e}")
        return out

    def fetch_comments(self, video_id: str, max_comments: int = 200) -> list[dict]:
        svc = self._svc()
        comments = []
        page_token = None
        try:
            while len(comments) < max_comments:
                req = svc.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,
                    pageToken=page_token,
                    textFormat="plainText",
                    order="relevance"
                )
                resp = req.execute()
                for it in resp.get("items", []):
                    top = it["snippet"]["topLevelComment"]["snippet"]
                    comments.append({
                        "comment_id": it.get("id"),
                        "text": top.get("textDisplay", ""),
                        "author": top.get("authorDisplayName", ""),
                        "likeCount": top.get("likeCount", 0),
                        "publishedAt": top.get("publishedAt", ""),
                    })
                    if len(comments) >= max_comments:
                        break
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break
        except Exception as e:
            # gracefully handle videos with disabled comments or quota issues
            print(f"[WARN] Could not fetch comments for video {video_id}: {e}")
        return comments

