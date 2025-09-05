# Smart Fan Share of Voice (SoV) Agent

This repo implements an AI agent that:
1. Searches **YouTube** for given keywords such as "smart fan".
2. Collects the **top N** results for each keyword.
3. Extracts mentions of **Atomberg** and competitors in titles, descriptions, and comments.
4. Computes SoV and **Share of Positive Voice** using VADER sentiment on comment text.
5. Outputs tidy CSVs and a one-click **insights report**.

> ⚙️ The project prioritizes YouTube (official API, stable access). You can plug in Google/Instagram/X with the same interface later.

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# one-time: download VADER lexicon
python -c "import nltk; nltk.download('vader_lexicon')"

# env
cp .env.example .env  # fill in YOUTUBE_API_KEY

# run
python src/main.py --keywords-file data/keywords.txt --top-n 30 --days 365
```

Outputs land in `reports/` and `reports/exports/`.

---

## Design

- **Platforms**: pluggable `PlatformClient` interfaces; we ship `YouTubeClient` today.
- **Brand Matching**: case-insensitive exact + fuzzy token matches with allowlists/blocklists.
- **Sentiment**: VADER (fast, no GPU). Can swap to Transformers later.
- **Metrics**:
  - **SoV** = weighted share of brand mentions across results, where each result weight is a function of engagement.
  - **Share of Positive Voice (SPV)** = proportion of *positive* brand-mention comments for a brand.
- **Reproducibility**: All inputs/outputs versioned timestamps, parameters stored in `run_config.json`.

---

## Two-Pager
We generate a template in `reports/Submission_Two_Pager_Template.pdf`. Fill it after a run using the CSVs from `reports/exports/`.

---

## Extending to other platforms

Implement `PlatformClient` with methods:
- `search(query, max_results, published_after)`
- `fetch_comments(content_id, max_comments)`
- Return a normalized payload like `NormalizedPost` (see code).

Then add it to `src/pipeline.py` with a simple registry entry.
