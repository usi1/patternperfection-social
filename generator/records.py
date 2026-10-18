"""Print the Make data store records for a week spec, as JSON.

Usage: python3 generator/records.py weeks/2026-10-19.json

Each record: {"key": "<YYYY-MM-DD>", "data": {...}} for data store
"Pattern Perfection – calendario social" (id 223833).
Image URLs point at the public raw files on the main branch, so push first.
"""
import json
import sys
from pathlib import Path

RAW = "https://raw.githubusercontent.com/usi1/patternperfection-social/main/posts"

spec = json.loads(Path(sys.argv[1]).read_text())
records = []
for post in spec["posts"]:
    n = len(post["slides"])
    records.append({
        "key": post["date"],
        "data": {
            "format": post["format"],
            "topic": post["topic"],
            "caption_ig": post["caption_ig"],
            "caption_fb": post["caption_fb"],
            "images": [{"url": f"{RAW}/{post['date']}/{i:02d}.jpg"} for i in range(1, n + 1)],
            "status": "scheduled",
        },
    })
print(json.dumps(records, ensure_ascii=False, indent=2))
