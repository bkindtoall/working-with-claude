"""Build the GitHub Pages copy and the WordPress embed from index.html (the one source).

    python3 build.py

docs/index.html          standalone page for GitHub Pages (Settings > Pages > main /docs)
wordpress/embed.html     paste into an Elementor HTML widget on craftingmetrics.com.
                         Renders inside a shadow root, so the site theme and the page
                         cannot restyle each other. Light mode only, to sit on the site.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
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
wp = HERE / "wordpress"
wp.mkdir(exist_ok=True)
tpl = f"""{fonts}
<div id="cm-logbook"></div>
<template id="cm-logbook-tpl"><style>{light}</style>{body}</template>
<script>
(function(){{
  var host = document.getElementById("cm-logbook");
  var root = host.attachShadow({{mode: "open"}});
  root.appendChild(document.getElementById("cm-logbook-tpl").content.cloneNode(true));
  {shadow_js}
}})();
</script>
"""
(wp / "embed.html").write_text(tpl)
print(f"docs/index.html {len((docs / 'index.html').read_text()):,} bytes; wordpress/embed.html {len(tpl):,} bytes")
