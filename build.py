#!/usr/bin/env python3
"""Builds the Ripline support site from the Markdown in ../Docs.

Run it after editing either Markdown file:

    python3 Site/build.py

The Markdown files stay the source of truth so the pages can't drift from
what the repo says. The converter handles only the subset of Markdown those
two documents use — headings, bold, inline code, links, ordered and unordered
lists, and paragraphs — and fails loudly on anything it doesn't recognise
rather than emitting half-rendered text.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT.parent / "Docs"
CONFIG = json.loads((ROOT / "site.json").read_text())

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="bar">
  <a class="wordmark" href="./">Ripline</a>
  <nav>
    <a href="privacy.html"{privacy_current}>Privacy</a>
    <a href="support.html"{support_current}>Support</a>
  </nav>
</header>
<main>
{body}
</main>
<footer>
  <p>Ripline is a paid iPhone app. One price, every feature, no subscription.</p>
  <p class="muted">Last updated {updated}.</p>
</footer>
</body>
</html>
"""

# The text is HTML-escaped before these run, so nothing here escapes again.
INLINE = (
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{m.group(1)}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>'),
)


def inline(text: str) -> str:
    """Escapes, then applies the inline markup, then fills in the email."""
    out = html.escape(text)
    for pattern, repl in INLINE:
        out = pattern.sub(repl, out)
    email = CONFIG["supportEmail"]
    return out.replace("{{EMAIL}}", f'<a href="mailto:{email}">{email}</a>')


def convert(markdown: str) -> tuple[str, str]:
    """Returns (page title, body HTML)."""
    title = ""
    parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag = ""

    def flush_paragraph() -> None:
        if paragraph:
            parts.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_items:
            items = "".join(f"<li>{inline(item)}</li>" for item in list_items)
            parts.append(f"<{list_tag}>{items}</{list_tag}>")
            list_items.clear()
            list_tag = ""

    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = inline(heading.group(2))
            if level == 1 and not title:
                title = re.sub(r"<[^>]+>", "", text)
                parts.append(f"<h1>{text}</h1>")
            else:
                parts.append(f"<h{level}>{text}</h{level}>")
            continue

        bullet = re.match(r"^[-*]\s+(.*)$", line)
        numbered = re.match(r"^\d+\.\s+(.*)$", line)
        if bullet or numbered:
            flush_paragraph()
            wanted = "ul" if bullet else "ol"
            if list_tag and list_tag != wanted:
                flush_list()
            list_tag = wanted
            list_items.append((bullet or numbered).group(1))
            continue

        if line.startswith("  ") and list_items:
            list_items[-1] += " " + line.strip()
            continue

        flush_list()
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    return title, "\n".join(parts)


def render(source: pathlib.Path, output: pathlib.Path, description: str) -> None:
    title, body = convert(source.read_text())
    page = TEMPLATE.format(
        title=f"{title} — Ripline" if "Ripline" not in title else title,
        description=description,
        body=body,
        updated=CONFIG["updated"],
        privacy_current=' class="current"' if output.name == "privacy.html" else "",
        support_current=' class="current"' if output.name == "support.html" else "",
    )
    output.write_text(page)
    print(f"wrote {output.relative_to(ROOT.parent)}")


def main() -> int:
    if "EMAIL" in CONFIG["supportEmail"] or "@" not in CONFIG["supportEmail"]:
        print("site.json has no real support address yet — refusing to build", file=sys.stderr)
        return 1
    render(DOCS / "PRIVACY_POLICY.md", ROOT / "privacy.html",
           "Ripline collects nothing: no account, no analytics, no tracking.")
    render(DOCS / "SUPPORT.md", ROOT / "support.html",
           "Help for Ripline, the cut list optimizer for iPhone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
