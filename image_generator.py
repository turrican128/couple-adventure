import re
import tempfile
from datetime import datetime
from pathlib import Path

import cv2
import fal_client
import numpy as np
import requests


def _create_face_reference(image_path: str) -> str:
    """
    Detect both faces in the couple photo, crop them with padding,
    and stitch side-by-side into a composite reference image.
    Falls back to the original image if fewer than 2 faces are found.
    Returns path to the reference image to use.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) < 2:
        print("  [face-ref] fewer than 2 faces detected — using original photo as reference")
        return image_path

    # Take the 2 largest faces, sorted left-to-right for consistency
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[:2]
    faces = sorted(faces, key=lambda f: f[0])

    h, w = img.shape[:2]
    crops = []
    for (x, y, fw, fh) in faces:
        pad = int(max(fw, fh) * 0.5)
        x1, y1 = max(0, x - pad), max(0, y - pad)
        x2, y2 = min(w, x + fw + pad), min(h, y + fh + pad)
        crop = cv2.resize(img[y1:y2, x1:x2], (512, 512))
        crops.append(crop)

    composite = np.hstack(crops)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    cv2.imwrite(tmp.name, composite)
    print(f"  [face-ref] composite face reference created ({len(faces)} faces detected)")
    return tmp.name


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

    # Build a face-focused composite reference and upload it
    reference_path = _create_face_reference(image_path)
    image_url = fal_client.upload_file(reference_path)

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
