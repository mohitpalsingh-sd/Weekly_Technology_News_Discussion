import datetime as dt
import pathlib
import yaml
import feedparser

# --- CONFIG ---
DAYS = 7
now = dt.datetime.now(dt.timezone.utc)
cutoff = now - dt.timedelta(days=DAYS)

# --- LOAD SOURCES ---
BASE = pathlib.Path(__file__).parent
sources_path = BASE / "sources.yml"

with open(sources_path, "r") as f:
    sources = yaml.safe_load(f)["sources"]

# --- OUTPUT ---
lines = [
    f"# Weekly Tech Digest — {now:%Y-%m-%d}\n",
    f"_Articles from the last {DAYS} days_\n"
]

# --- PROCESS FEEDS ---
for s in sources:
    feed = feedparser.parse(s["url"])

    if feed.bozo:
        lines.append(f"\n## {s['name']}\n\nCould not parse feed ({s['url']})\n")
        continue

    recent = []

    for e in feed.entries:
        t = e.get("published_parsed") or e.get("updated_parsed")
        if not t:
            continue

        pub = dt.datetime(*t[:6], tzinfo=dt.timezone.utc)

        if pub >= cutoff:
            recent.append(
                (pub, e.get("title", "Untitled"), e.get("link", ""))
            )

    lines.append(f"\n## {s['name']}\n")

    if not recent:
        lines.append("\n_No new articles this week._\n")
    else:
        for pub, title, link in sorted(recent, reverse=True):
            lines.append(f"- [{title}]({link}) — {pub:%Y-%m-%d}")

# --- WRITE FILE ---
out_dir = BASE / "digests"
out_dir.mkdir(exist_ok=True)

out_file = out_dir / f"{now:%Y-%m-%d}.md"
out_file.write_text("\n".join(lines), encoding="utf-8")

print(f"Wrote {out_file}")
