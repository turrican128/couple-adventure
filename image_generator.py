import re
from datetime import datetime
from pathlib import Path

import fal_client
import requests


def _make_slug(text: str, max_len: int = 50) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:max_len].rstrip("-")


def generate_image(image_path: str, prompt: str, output_dir: str = "output", scenario: str = "") -> str:
    """
    Upload the couple photo to fal.ai and use FLUX Kontext to transform
    the scene while keeping both people's faces exactly as they are.
    Returns path to the saved result image.
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(
            f"Couple image not found: {image_path}\n"
            "Please add your couple photo to the images/ folder."
        )

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Upload the couple photo as the base image to edit
    image_url = fal_client.upload_file(image_path)

    result = fal_client.subscribe(
        "fal-ai/flux-kontext/dev",
        arguments={
            "image_url": image_url,
            "prompt": prompt,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "output_format": "jpeg",
        },
    )

    generated_url = result["images"][0]["url"]

    response = requests.get(generated_url)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = f"_{_make_slug(scenario)}" if scenario else ""
    output_path = str(Path(output_dir) / f"{timestamp}{slug}.jpg")
    Path(output_path).write_bytes(response.content)

    return output_path
