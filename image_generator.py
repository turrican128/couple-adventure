import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

import cv2
import fal_client
import numpy as np
import requests

# Genders of the two people in the photo (left-to-right order).
# Set PERSON_1_GENDER and PERSON_2_GENDER in your .env file.
_PERSON_1_GENDER = os.getenv("PERSON_1_GENDER", "female")
_PERSON_2_GENDER = os.getenv("PERSON_2_GENDER", "male")


def _crop_faces(image_path: str) -> list:
    """
    Detect both faces and return paths to individual face crops [left, right].
    Returns empty list if fewer than 2 faces are found.
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) < 2:
        print("  [face-swap] fewer than 2 faces detected — skipping face swap")
        return []

    # Take the 2 largest, sorted left-to-right
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[:2]
    faces = sorted(faces, key=lambda f: f[0])

    h, w = img.shape[:2]
    paths = []
    for (x, y, fw, fh) in faces:
        pad = int(max(fw, fh) * 0.5)
        x1, y1 = max(0, x - pad), max(0, y - pad)
        x2, y2 = min(w, x + fw + pad), min(h, y + fh + pad)
        crop = img[y1:y2, x1:x2]
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        cv2.imwrite(tmp.name, crop)
        paths.append(tmp.name)

    return paths


def _apply_face_swap(generated_path: str, face_paths: list) -> str:
    """
    Swap both faces from the original couple photo into the generated image.
    Overwrites generated_path with the result. Returns generated_path.
    """
    print("  [face-swap] uploading images...")
    generated_url = fal_client.upload_file(generated_path)
    face0_url = fal_client.upload_file(face_paths[0])
    face1_url = fal_client.upload_file(face_paths[1])

    print("  [face-swap] running face swap (this may take a moment)...")
    result = fal_client.subscribe(
        "easel-ai/advanced-face-swap",
        arguments={
            "face_image_0": {"url": face0_url},
            "gender_0": _PERSON_1_GENDER,
            "face_image_1": {"url": face1_url},
            "gender_1": _PERSON_2_GENDER,
            "target_image": {"url": generated_url},
            "workflow_type": "target_hair",
            "upscale": True,
        },
    )

    swapped_url = result["image"]["url"]
    response = requests.get(swapped_url)
    response.raise_for_status()
    Path(generated_path).write_bytes(response.content)
    print("  [face-swap] done")
    return generated_path


def _make_slug(text: str, max_len: int = 50) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:max_len].rstrip("-")


def generate_image(image_path: str, prompt: str, output_dir: str = "output", scenario: str = "") -> str:
    """
    1. Generate scene with InstantCharacter using the couple photo.
    2. Swap both faces from the original into the result for consistency.
    Returns path to the final saved image.
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(
            f"Couple image not found: {image_path}\n"
            "Please add your couple photo to the images/ folder."
        )

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Step 1 — Generate scene
    image_url = fal_client.upload_file(image_path)
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
    response = requests.get(generated_url)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug = f"_{_make_slug(scenario)}" if scenario else ""
    output_path = str(Path(output_dir) / f"{timestamp}{slug}.jpg")
    Path(output_path).write_bytes(response.content)

    # Step 2 — Swap both faces for consistency
    face_paths = _crop_faces(image_path)
    if len(face_paths) == 2:
        _apply_face_swap(output_path, face_paths)

    return output_path
