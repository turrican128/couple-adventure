"""
Opens a local HTML gallery of all generated couple adventure images.
Run: python gallery.py
"""
import html
import webbrowser
from pathlib import Path

OUTPUT_DIR = Path("output")
GALLERY_FILE = Path("gallery.html")


def read_scenario(log_path: Path) -> str:
    """Returns the scenario text from a per-image .txt log file, or empty string."""
    if not log_path.exists():
        return ""

    lines = log_path.read_text(encoding="utf-8").splitlines()
    scenario_lines = []
    reading = False
    for line in lines:
        if line.strip() == "Scenario:":
            reading = True
        elif line.strip() == "Image Prompt:":
            break
        elif reading and line.strip():
            scenario_lines.append(line.strip())
    return " ".join(scenario_lines).strip()


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
        f'<div class="card">'
        f'<img src="{html.escape(img.as_posix())}" loading="lazy">'
        f'<div class="info">'
        f'<p class="stem">{html.escape(img.stem)}</p>'
        + (f'<p class="scenario">{html.escape(scenario)}</p>' if (scenario := read_scenario(img.with_suffix(".txt"))) else "")
        + "</div></div>"
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
    .info {{ padding: 10px 12px; }}
    .stem {{ font-size: 11px; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }}
    .scenario {{ font-size: 12px; color: #ccc; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }}
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
