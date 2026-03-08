#!/usr/bin/env python3
"""Generate rendered HTML docs pages from markdown sources.

Each docs/*.md file gets a rendered /docs/<slug>/index.html page.
Internal .md links are rewritten to clean /docs/<slug>/ routes.
A "view raw markdown" link is included for agent/source access.

Usage:
    python scripts/gen_docs_html.py
"""

import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")

# Docs to generate (slug derived from filename minus .md)
DOCS = [
    "setup-guide",
    "openclaw-integration",
    "reproduce-eval",
    "worked-example",
    "operator-guide",
    "ops-recipes",
    "new-agent-sop",
    "secrets-and-capabilities",
    "brains-dashboard",
]

# Human-readable titles for each doc
TITLES = {
    "setup-guide": "Setup Guide",
    "openclaw-integration": "OpenClaw Integration",
    "reproduce-eval": "Reproduce Eval",
    "worked-example": "Worked Example",
    "operator-guide": "Operator Guide",
    "ops-recipes": "Ops Recipes",
    "new-agent-sop": "New Agent SOP",
    "secrets-and-capabilities": "Secrets and Capabilities",
    "brains-dashboard": "Brains Dashboard",
}


def fix_internal_links(html: str) -> str:
    """Rewrite internal .md links to rendered /docs/<slug>/ routes,
    and replace visible labels like 'docs/setup-guide.md' with human titles."""
    def replace_md_link(m):
        prefix = m.group(1)
        filename = m.group(2)
        slug = filename.replace(".md", "")
        return f'{prefix}/docs/{slug}/'
    # Match href="<optional-path>some-file.md" for known doc files
    html = re.sub(
        r'(href=["\'])(?:\.\.\/docs\/|\/docs\/|\.\/)?([a-z0-9_-]+\.md)',
        replace_md_link,
        html,
        flags=re.IGNORECASE,
    )
    # Replace visible link labels like "docs/setup-guide.md" with human titles
    def replace_md_label(m):
        full = m.group(0)
        slug = m.group(1)
        title = TITLES.get(slug, slug.replace("-", " ").title())
        return full.replace(f'docs/{slug}.md', title).replace(f'{slug}.md', title)
    html = re.sub(
        r'<a\s[^>]*>[^<]*?(?:docs/)?([a-z0-9_-]+)\.md[^<]*</a>',
        replace_md_label,
        html,
        flags=re.IGNORECASE,
    )
    return html


def markdown_to_html(md_text: str) -> str:
    """Convert markdown to HTML. Uses the markdown library if available,
    otherwise does a basic conversion."""
    try:
        import markdown
        return markdown.markdown(
            md_text,
            extensions=["tables", "fenced_code", "codehilite", "toc"],
        )
    except ImportError:
        # Fallback: basic conversion
        html = md_text
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        # Code blocks
        html = re.sub(
            r'```(\w*)\n(.*?)```',
            r'<pre><code>\2</code></pre>',
            html,
            flags=re.DOTALL,
        )
        # List items
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        # Wrap consecutive <li> in <ul>
        html = re.sub(
            r'((?:<li>.*?</li>\n?)+)',
            r'<ul>\1</ul>',
            html,
        )
        # Paragraphs (blank-line separated)
        parts = html.split('\n\n')
        result = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.startswith('<'):
                result.append(part)
            else:
                result.append(f'<p>{part}</p>')
        html = '\n'.join(result)
        return html


TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — OpenClawBrain</title>
  <meta name="description" content="{title} documentation for OpenClawBrain." />
  <link rel="canonical" href="https://openclawbrain.ai/docs/{slug}/" />
  <style>
    :root {{
      --bg:#0a0f17;
      --card:#111a27;
      --text:#d6dfed;
      --muted:#93a1b7;
      --bright:#f5f8ff;
      --border:#26344a;
      --accent:#79b7ff;
      --sans:Inter,system-ui,sans-serif;
      --serif:"Crimson Pro",Georgia,serif;
      --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
    }}
    * {{ box-sizing:border-box; }}
    body {{
      margin:0;
      background:radial-gradient(circle at 15% 0%,#152137,#0a0f17 45%);
      color:var(--text);
      font-family:var(--serif);
      line-height:1.75;
    }}
    main {{ max-width:860px; margin:0 auto; padding:2.8rem 1.2rem 4rem; }}
    h1,h2,h3 {{ font-family:var(--sans); color:var(--bright); margin:1.4rem 0 .6rem; }}
    h1 {{ margin-top:0; }}
    p {{ margin:0 0 1rem; }}
    a {{ color:var(--accent); }}
    ul,ol {{ margin:0 0 1.2rem; padding-left:1.4rem; }}
    li {{ margin:.3rem 0; }}
    code {{ font-family:var(--mono); font-size:.9em; background:rgba(121,183,255,.1); padding:.15em .35em; border-radius:4px; }}
    pre {{ overflow-x:auto; background:#0d1321; border:1px solid var(--border); border-radius:8px; padding:1rem; margin:1rem 0 1.4rem; }}
    pre code {{ background:none; padding:0; font-size:.85em; color:#c7d2fe; }}
    table {{ border-collapse:collapse; width:100%; margin:1rem 0 1.4rem; }}
    th,td {{ text-align:left; padding:.5rem .7rem; border:1px solid var(--border); }}
    th {{ background:var(--card); font-family:var(--sans); color:var(--bright); font-size:.9rem; }}
    .nav {{ font-family:var(--sans); color:var(--muted); font-size:.86rem; margin-bottom:1.4rem; }}
    .source-link {{ font-family:var(--sans); font-size:.82rem; color:var(--muted); margin-top:2rem; padding-top:1rem; border-top:1px solid var(--border); }}
    .source-link a {{ color:var(--muted); }}
    .source-link a:hover {{ color:var(--accent); }}
    img {{ max-width:100%; height:auto; border-radius:10px; border:1px solid var(--border); }}
    @media (max-width:600px) {{
      main {{ padding:1.6rem .8rem 2.4rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <div class="nav"><a href="/">openclawbrain.ai</a> / <a href="/docs/setup-guide/">docs</a></div>
    <h1>{title}</h1>
    {body}
    <div class="source-link">
      <a href="/docs/{slug}.md">View source (Markdown)</a>
    </div>
  </main>
</body>
</html>
"""


def generate_doc(slug: str) -> None:
    md_path = os.path.join(DOCS_DIR, f"{slug}.md")
    if not os.path.exists(md_path):
        print(f"  SKIP {slug}: {md_path} not found")
        return

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    title = TITLES.get(slug, slug.replace("-", " ").title())

    # Strip leading H1 (the template adds its own)
    md_text = re.sub(r'^# .+\n+', '', md_text, count=1)

    # Strip self-referential "Note: HTML version at ..." lines
    md_text = re.sub(r'^Note: HTML version at .+\n+', '', md_text, count=1)

    # Convert markdown to HTML
    body_html = markdown_to_html(md_text)

    # Rewrite internal .md links to clean routes
    body_html = fix_internal_links(body_html)

    # Build full page
    page_html = TEMPLATE.format(
        title=title,
        slug=slug,
        body=body_html,
    )

    # Write output
    out_dir = os.path.join(DOCS_DIR, slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_html)
    print(f"  OK {slug} -> {os.path.relpath(out_path, REPO_ROOT)}")


def main():
    print("Generating rendered docs pages...")
    for slug in DOCS:
        generate_doc(slug)
    print("Done.")


if __name__ == "__main__":
    main()
