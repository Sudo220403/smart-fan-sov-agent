import argparse, sys, json, os
from pathlib import Path
from src.config import AppConfig
from src.pipeline import SovPipeline


def read_keywords(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    p = argparse.ArgumentParser(description="Smart Fan SoV Agent (YouTube)")
    p.add_argument("--keywords-file", type=str, default="data/keywords.txt")
    p.add_argument("--top-n", type=int, default=30)
    p.add_argument("--days", type=int, default=365, help="Lookback window for content publish date")
    p.add_argument("--out", type=str, default="reports")
    args = p.parse_args()

    cfg = AppConfig()
    if not cfg.youtube_api_key:
        print("ERROR: Please set YOUTUBE_API_KEY in .env", file=sys.stderr)
        sys.exit(2)

    keywords = read_keywords(args.keywords_file)
    pipe = SovPipeline(cfg, out_dir=args.out)
    run_cfg = pipe.run(keywords, top_n=args.top_n, days=args.days)

    print("Run complete. Exports:")
    print(json.dumps(run_cfg["exports"], indent=2))

if __name__ == "__main__":
    main()
