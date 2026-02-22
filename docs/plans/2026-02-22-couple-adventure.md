# Couple Adventure Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python script that generates a face-preserving image of a real couple in a new random creative scenario every time it is run.

**Architecture:** Claude API generates a fresh creative scenario + image prompt each run. The couple photo is uploaded to fal.ai storage, then passed to the InstantID model along with the prompt to produce a face-preserving output image, which is saved locally with a timestamp.

**Tech Stack:** Python 3.10+, `anthropic` SDK, `fal-client` SDK, `python-dotenv`, `requests`, `pytest`

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `tests/__init__.py`

**Step 1: Create requirements.txt**

```
anthropic>=0.40.0
fal-client>=0.5.0
python-dotenv>=1.0.0
requests>=2.31.0
pytest>=8.0.0
```

**Step 2: Create .gitignore**

```
.env
output/
__pycache__/
*.pyc
.pytest_cache/
```

**Step 3: Create .env.example**

```
ANTHROPIC_API_KEY=your_anthropic_key_here
FAL_KEY=your_fal_key_here
```

**Step 4: Create tests/__init__.py**

Empty file. Just `touch tests/__init__.py`.

**Step 5: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install without error.

**Step 6: Commit**

```bash
git init
git add requirements.txt .gitignore .env.example tests/__init__.py docs/
git commit -m "feat: initial project scaffolding"
```

---

### Task 2: Environment Config Module

**Files:**
- Create: `tests/test_config.py`
- Create: `config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import os
import pytest
from unittest.mock import patch


def test_load_config_returns_both_keys():
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-ant", "FAL_KEY": "test-fal"}):
        from config import load_config
        cfg = load_config()
        assert cfg["anthropic_api_key"] == "test-ant"
        assert cfg["fal_key"] == "test-fal"


def test_load_config_raises_if_anthropic_key_missing():
    env = {"FAL_KEY": "test-fal"}
    with patch.dict(os.environ, env, clear=True):
        # remove ANTHROPIC_API_KEY if present
        os.environ.pop("ANTHROPIC_API_KEY", None)
        import importlib, config
        importlib.reload(config)
        from config import load_config
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            load_config()


def test_load_config_raises_if_fal_key_missing():
    env = {"ANTHROPIC_API_KEY": "test-ant"}
    with patch.dict(os.environ, env, clear=True):
        os.environ.pop("FAL_KEY", None)
        import importlib, config
        importlib.reload(config)
        from config import load_config
        with pytest.raises(ValueError, match="FAL_KEY"):
            load_config()
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'config'`

**Step 3: Write minimal implementation**

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()


def load_config() -> dict:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    fal_key = os.getenv("FAL_KEY")

    if not anthropic_key:
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")
    if not fal_key:
        raise ValueError("FAL_KEY is not set. Add it to your .env file.")

    return {
        "anthropic_api_key": anthropic_key,
        "fal_key": fal_key,
    }
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```

Expected: All 3 tests PASS.

**Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add config module with env validation"
```

---

### Task 3: Scenario Generator

**Files:**
- Create: `tests/test_scenario_generator.py`
- Create: `scenario_generator.py`

**Step 1: Write the failing test**

```python
# tests/test_scenario_generator.py
import pytest
from unittest.mock import MagicMock, patch


def _make_mock_client(json_text: str):
    """Helper: returns a mock Anthropic client that returns json_text."""
    mock_content = MagicMock()
    mock_content.text = json_text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_generate_scenario_returns_scenario_and_prompt():
    json_response = '{"scenario": "The couple is skydiving over the Grand Canyon.", "image_prompt": "A couple skydiving at sunset, wide angle shot."}'
    mock_client = _make_mock_client(json_response)

    with patch("scenario_generator.Anthropic", return_value=mock_client):
        from scenario_generator import generate_scenario
        result = generate_scenario(api_key="fake-key")

    assert "scenario" in result
    assert "image_prompt" in result
    assert isinstance(result["scenario"], str)
    assert isinstance(result["image_prompt"], str)


def test_generate_scenario_raises_on_invalid_json():
    mock_client = _make_mock_client("not valid json")

    with patch("scenario_generator.Anthropic", return_value=mock_client):
        from scenario_generator import generate_scenario
        with pytest.raises(ValueError, match="Failed to parse"):
            generate_scenario(api_key="fake-key")


def test_generate_scenario_raises_on_missing_fields():
    mock_client = _make_mock_client('{"scenario": "something"}')

    with patch("scenario_generator.Anthropic", return_value=mock_client):
        from scenario_generator import generate_scenario
        with pytest.raises(ValueError, match="image_prompt"):
            generate_scenario(api_key="fake-key")
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_scenario_generator.py -v
```

Expected: `ModuleNotFoundError: No module named 'scenario_generator'`

**Step 3: Write minimal implementation**

```python
# scenario_generator.py
import json
import re
from anthropic import Anthropic

SYSTEM_PROMPT = """You are a wildly creative director for a couple's adventure photo series.
Your job is to invent unique, vivid, and visually striking scenarios where a real couple is placed.
Think big: exotic locations, extraordinary activities, fantasy settings, historical moments, or absurd fun.
Each scenario must be visually distinctive and feel like a real photograph moment."""

USER_PROMPT = """Generate a completely random and creative scenario for a couple's adventure photo.

Return ONLY a valid JSON object with this exact structure (no other text):
{
  "scenario": "A short 1-2 sentence description of the scenario for display",
  "image_prompt": "A detailed photorealistic image generation prompt. Start with 'A couple' and describe what they are doing, the setting, lighting, atmosphere, camera angle, and visual style. Be specific and vivid. Aim for 3-5 sentences."
}"""


def generate_scenario(api_key: str) -> dict:
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Claude response as JSON: {e}\nResponse was: {raw}")

    for field in ("scenario", "image_prompt"):
        if field not in data:
            raise ValueError(f"Claude response missing required field '{field}'. Got: {data}")

    return data
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_scenario_generator.py -v
```

Expected: All 3 tests PASS.

**Step 5: Commit**

```bash
git add scenario_generator.py tests/test_scenario_generator.py
git commit -m "feat: add scenario generator using Claude API"
```

---

### Task 4: Image Generator

**Files:**
- Create: `tests/test_image_generator.py`
- Create: `image_generator.py`

**Step 1: Write the failing test**

```python
# tests/test_image_generator.py
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_generate_image_saves_file(tmp_path):
    fake_image_bytes = b"\xff\xd8\xff"  # minimal JPEG header

    mock_response = MagicMock()
    mock_response.json.return_value = {"images": [{"url": "https://example.com/img.jpg"}]}
    mock_response.raise_for_status = MagicMock()
    mock_response.content = fake_image_bytes

    with patch("image_generator.fal_client") as mock_fal, \
         patch("image_generator.requests.get", return_value=mock_response):

        mock_fal.upload_file.return_value = "https://fal.ai/tmp/couple.jpg"
        mock_fal.subscribe.return_value = {"images": [{"url": "https://example.com/img.jpg"}]}

        from image_generator import generate_image
        output_path = generate_image(
            image_path="images/couple.jpg",
            prompt="A couple skydiving over the Grand Canyon at sunset.",
            output_dir=str(tmp_path),
        )

    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".jpg"
    assert Path(output_path).read_bytes() == fake_image_bytes


def test_generate_image_raises_if_input_missing(tmp_path):
    from image_generator import generate_image
    with pytest.raises(FileNotFoundError, match="images/nonexistent.jpg"):
        generate_image(
            image_path="images/nonexistent.jpg",
            prompt="test",
            output_dir=str(tmp_path),
        )
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_image_generator.py -v
```

Expected: `ModuleNotFoundError: No module named 'image_generator'`

**Step 3: Write minimal implementation**

```python
# image_generator.py
import os
from datetime import datetime
from pathlib import Path

import fal_client
import requests


def generate_image(image_path: str, prompt: str, output_dir: str = "output") -> str:
    """
    Upload couple image to fal.ai, run InstantID with prompt,
    download result, and save to output_dir. Returns path to saved file.
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(
            f"Couple image not found: {image_path}\n"
            "Please add your couple photo to the images/ folder."
        )

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Upload reference image to fal.ai temporary storage
    image_url = fal_client.upload_file(image_path)

    # Call InstantID
    result = fal_client.subscribe(
        "fal-ai/instant-id",
        arguments={
            "face_image_url": image_url,
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted face, deformed, ugly, bad anatomy",
            "guidance_scale": 5.0,
            "num_inference_steps": 30,
        },
    )

    generated_url = result["images"][0]["url"]

    # Download the result image
    response = requests.get(generated_url)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = str(Path(output_dir) / f"{timestamp}.jpg")
    Path(output_path).write_bytes(response.content)

    return output_path
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_image_generator.py -v
```

Expected: All 2 tests PASS.

**Step 5: Commit**

```bash
git add image_generator.py tests/test_image_generator.py
git commit -m "feat: add image generator using fal.ai InstantID"
```

---

### Task 5: Main Entry Point

**Files:**
- Create: `tests/test_main.py`
- Create: `main.py`

**Step 1: Write the failing test**

```python
# tests/test_main.py
from unittest.mock import patch, MagicMock


def test_main_happy_path(tmp_path):
    fake_scenario = {
        "scenario": "The couple is riding elephants through a jungle.",
        "image_prompt": "A couple riding elephants through a lush jungle at golden hour.",
    }
    fake_output_path = str(tmp_path / "2026-01-01_12-00-00.jpg")

    with patch("main.load_config", return_value={"anthropic_api_key": "a", "fal_key": "f"}), \
         patch("main.get_couple_image_path", return_value="images/couple.jpg"), \
         patch("main.generate_scenario", return_value=fake_scenario), \
         patch("main.generate_image", return_value=fake_output_path) as mock_gen_img:

        from main import run
        run()

    mock_gen_img.assert_called_once_with(
        image_path="images/couple.jpg",
        prompt=fake_scenario["image_prompt"],
    )


def test_get_couple_image_path_finds_jpg(tmp_path):
    img = tmp_path / "couple.jpg"
    img.write_bytes(b"fake")

    from main import get_couple_image_path
    result = get_couple_image_path(images_dir=str(tmp_path))
    assert result == str(img)


def test_get_couple_image_path_raises_if_empty(tmp_path):
    import pytest
    from main import get_couple_image_path
    with pytest.raises(FileNotFoundError, match="No image found"):
        get_couple_image_path(images_dir=str(tmp_path))
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_main.py -v
```

Expected: `ModuleNotFoundError: No module named 'main'`

**Step 3: Write minimal implementation**

```python
# main.py
import os
from pathlib import Path

from config import load_config
from scenario_generator import generate_scenario
from image_generator import generate_image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_couple_image_path(images_dir: str = "images") -> str:
    for ext in SUPPORTED_EXTENSIONS:
        matches = list(Path(images_dir).glob(f"*{ext}"))
        if matches:
            return str(matches[0])
    raise FileNotFoundError(
        f"No image found in '{images_dir}/' folder.\n"
        "Please add your couple photo (JPG, PNG, or WEBP) to the images/ folder."
    )


def run():
    print("Couple Adventure Generator")
    print("-" * 40)

    cfg = load_config()

    image_path = get_couple_image_path()
    print(f"Using image: {image_path}")

    print("Generating scenario...")
    scenario_data = generate_scenario(api_key=cfg["anthropic_api_key"])

    print(f"\nScenario: {scenario_data['scenario']}\n")
    print("Generating image (this may take 20-40 seconds)...")

    output_path = generate_image(
        image_path=image_path,
        prompt=scenario_data["image_prompt"],
    )

    print(f"\nDone! Image saved to: {output_path}")


if __name__ == "__main__":
    run()
```

**Step 4: Run all tests to verify everything passes**

```bash
pytest tests/ -v
```

Expected: All tests PASS.

**Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add main entry point"
```

---

### Task 6: README & GitHub Setup

**Files:**
- Create: `README.md`

**Step 1: Write README.md**

```markdown
# Couple Adventure Generator

Generates a new AI image of a real couple placed in a random creative scenario every time you run it. Faces are preserved using [fal.ai InstantID](https://fal.ai/models/fal-ai/instant-id). Scenarios are generated fresh each run by Claude.

## Setup

1. **Clone the repo and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your couple photo**
   Drop a JPG, PNG, or WEBP photo of the couple into the `images/` folder.

3. **Configure API keys**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   - `ANTHROPIC_API_KEY` — get from https://console.anthropic.com
   - `FAL_KEY` — get from https://fal.ai/dashboard

## Usage

```bash
python main.py
```

Each run generates a new image saved to `output/` with a timestamp filename. The scenario description is printed to the console.

## Example output

```
Couple Adventure Generator
----------------------------------------
Using image: images/couple.jpg
Generating scenario...

Scenario: The couple is dining underwater in a glass bubble restaurant surrounded by sharks.

Generating image (this may take 20-40 seconds)...

Done! Image saved to: output/2026-02-22_14-30-22.jpg
```
```

**Step 2: Connect to GitHub remote and push**

> Wait for the user to create the GitHub repo and share the URL, then run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/couple-adventure.git
git branch -M main
git push -u origin main
```

**Step 3: Verify on GitHub**

Open the repo URL in your browser and confirm all files are present.

---

## Full Test Run

After all tasks are complete, run the full test suite:

```bash
pytest tests/ -v
```

Expected: All tests PASS, zero failures.

Then do a real end-to-end run:

```bash
python main.py
```

Expected: A new image appears in `output/` and the scenario prints to the console.
