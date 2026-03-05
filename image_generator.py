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
    Upload couple image to fal.ai, run InstantCharacter with prompt,
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

    # Call InstantCharacter — preserves identity without locking in the reference pose
    result = fal_client.subscribe(
        "fal-ai/instant-character",
        arguments={
            "image_url": image_url,
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted face, deformed, ugly, bad anatomy, heart hands, silhouette, backs turned, facing away, from behind, faceless",
            "scale": 1.5,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
        },
    )

    generated_url = result["images"][0]["url"]

    # Download the result image
    response = requests.get(generated_url)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = f"_{_make_slug(scenario)}" if scenario else ""
    output_path = str(Path(output_dir) / f"{timestamp}{slug}.jpg")
    Path(output_path).write_bytes(response.content)

    return output_path
