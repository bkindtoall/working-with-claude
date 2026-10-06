"""Build the GitHub Pages copy and the WordPress embed from index.html (the one source).

    python3 build.py

docs/index.html          standalone page for GitHub Pages (Settings > Pages > main /docs)
docs/embed.js            the logbook for craftingmetrics.com, served from GitHub Pages.
                         Renders inside a shadow root, so the site theme and the page
                         cannot restyle each other. Light mode only, to sit on the site.
wordpress/embed.html     two-line snippet pasted ONCE into an Elementor HTML widget; it
                         loads docs/embed.js, so a push updates the site within minutes.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
PAGES = "https://bkindtoall.github.io/working-with-claude/"
src = (HERE / "index.html").read_text()

title = re.search(r"<title>.*?</title>", src).group(0)
fonts = "\n".join(re.findall(r"<link [^>]*>", src))
css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
body = re.search(r"</style>\s*(.*?)\s*<script>", src, re.S).group(1)
js = re.search(r"<script>(.*?)</script>", src, re.S).group(1)

# GitHub Pages: a full document around the same page.
docs = HERE / "docs"
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{title}
<meta name="description" content="Personal automations built with Claude, March to October 2026: an AI tool inventory, the upkeep behind it, and a logbook of what was built, fixed, replaced and retired.">
{fonts}
<style>body{{margin:0}}{css}</style>
</head>
<body>
{body}
<script>{js}</script>
</body>
</html>
""")

# WordPress: light palette only, :root -> :host, page body -> the host box.
light = re.sub(r"@media \(prefers-color-scheme: dark\)\{.*?\}\}", "", css, flags=re.S)
light = re.sub(r':root\[data-theme="dark"\]\{.*?\}', "", light, flags=re.S)
light = light.replace(":root{", ":host{").replace("body{", ":host{display:block;")
light = re.sub(r"top:env\(safe-area-inset-top,0px\)", "top:0", light)
shadow_js = js.replace("document.getElementById", "root.getElementById").replace(
    "document.querySelectorAll", "root.querySelectorAll")
# The embed script lives on GitHub Pages, so every push updates craftingmetrics.com too.
fonts_js = "".join(
    f'var l=document.createElement("link");l.rel="stylesheet";l.href={json.dumps(h)};document.head.appendChild(l);'
    for h in re.findall(r'<link rel="stylesheet" href="([^"]+)"', src))
(docs / "embed.js").write_text(f"""// Built by build.py from index.html. Loaded by the snippet in wordpress/embed.html.
(function(){{
  var host = document.getElementById("cm-logbook");
  if (!host || host.shadowRoot) return;
  {fonts_js}
  var root = host.attachShadow({{mode: "open"}});
  root.innerHTML = {json.dumps("<style>" + light + "</style>" + body)};
  {shadow_js}
}})();
""")
wp = HERE / "wordpress"
wp.mkdir(exist_ok=True)
tpl = f"""<div id="cm-logbook"></div>
<script src="{PAGES}embed.js" defer></script>
"""
(wp / "embed.html").write_text(tpl)
print(f"docs/index.html {len((docs / 'index.html').read_text()):,} bytes; docs/embed.js {len((docs / 'embed.js').read_text()):,} bytes")
