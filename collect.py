import datetime as dt
import pathlib
import yaml
import feedparser
from collections import defaultdict

# --- CONFIG ---
DAYS = 7
now = dt.datetime.now(dt.timezone.utc)
cutoff = now - dt.timedelta(days=DAYS)

TOPICS = {
    "AI / LLMs": [
        "ai", "llm", "gpt", "gemini", "transformer", "agent", "openai", "deepmind"
    ],
    "Linux / Kernel": [
        "linux", "kernel", "systemd", "driver", "nfs", "bpf", "dpdk"
    ],
    "Embedded / Yocto": [
        "yocto", "embedded", "arm", "jetson", "firmware", "rtos"
    ],
    "Web / Cloud": [
        "aws", "cloud", "kubernetes", "docker", "api", "serverless"
    ],
}

def classify(text: str) -> str:
    text = text.lower()
    for topic, keywords in TOPICS.items():
        if any(k in text for k in keywords):
            return topic
    return "Other"


# --- LOAD SOURCES ---
BASE = pathlib.Path(__file__).parent
sources_path = BASE / "sources.yml"

with open(sources_path, "r") as f:
    sources = yaml.safe_load(f)["sources"]

# --- DATA STRUCTURES ---
grouped = defaultdict(list)
seen = set()

# --- PROCESS FEEDS ---
for s in sources:
    feed = feedparser.parse(s["url"])

    if feed.bozo:
        grouped["Other"].append(
            f"- **{s['name']}**: Could not parse feed ({s['url']})"
        )
        continue

    for e in feed.entries:
        t = e.get("published_parsed") or e.get("updated_parsed")
        if not t:
            continue

        pub = dt.datetime(*t[:6], tzinfo=dt.timezone.utc)

        if pub < cutoff:
            continue

        title = e.get("title", "Untitled")
        link = e.get("link", "")

        # --- dedup ---
        if link in seen:
            continue
        seen.add(link)

        # --- classify ---
        topic = classify(f"{title} {s['name']}")

        grouped[topic].append(
            f"- [{title}]({link}) — {pub:%Y-%m-%d}"
        )

# --- BUILD OUTPUT ---
lines = [
    f"# Weekly Tech Digest — {now:%Y-%m-%d}\n",
    f"_Articles from the last {DAYS} days_\n"
]

# stable ordering
for topic in sorted(grouped.keys()):
    lines.append(f"\n## {topic}\n")

    items = grouped[topic]

    if not items:
        lines.append("_No articles_")
    else:
        lines.extend(items)

# --- WRITE FILE ---
out_dir = BASE / "digests"
out_dir.mkdir(exist_ok=True)

out_file = out_dir / f"{now:%Y-%m-%d}.md"
out_file.write_text("\n".join(lines), encoding="utf-8")

print(f"Wrote {out_file}")
