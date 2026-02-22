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
