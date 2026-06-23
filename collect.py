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
