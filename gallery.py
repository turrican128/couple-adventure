"""
Opens a local HTML gallery of all generated couple adventure images.
Run: python gallery.py
"""
import html
import webbrowser
from pathlib import Path

OUTPUT_DIR = Path("output")
GALLERY_FILE = Path("gallery.html")


def generate_gallery():
    images = sorted(
        [f for f in OUTPUT_DIR.glob("*") if f.suffix.lower() in {".jpg", ".jpeg", ".png"}],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )

    if not images:
        print("No images found in output/ folder. Run main.py first!")
        return

    cards = "\n".join(
        f'<div class="card"><img src="{html.escape(str(img))}" loading="lazy"><p>{html.escape(img.stem)}</p></div>'
        for img in images
    )

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Couple Adventure Gallery</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: #0f0f0f; color: #eee; font-family: sans-serif; padding: 24px; }}
    h1 {{ text-align: center; font-size: 2rem; margin-bottom: 4px; }}
    .subtitle {{ text-align: center; color: #888; margin-bottom: 24px; font-size: 0.9rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
    .card {{ background: #1a1a1a; border-radius: 12px; overflow: hidden; transition: transform 0.2s; }}
    .card:hover {{ transform: scale(1.02); }}
    .card img {{ width: 100%; display: block; aspect-ratio: 1; object-fit: cover; }}
    .card p {{ padding: 10px 12px; font-size: 11px; color: #999; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  </style>
</head>
<body>
  <h1>Couple Adventure Gallery</h1>
  <p class="subtitle">{len(images)} image{'s' if len(images) != 1 else ''} — newest first</p>
  <div class="grid">
{cards}
  </div>
</body>
</html>"""

    GALLERY_FILE.write_text(page, encoding="utf-8")
    url = GALLERY_FILE.resolve().as_uri()
    webbrowser.open(url)
    print(f"Gallery opened ({len(images)} images): {GALLERY_FILE.resolve()}")


if __name__ == "__main__":
    generate_gallery()
