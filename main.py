import sys
from pathlib import Path

from config import load_config
from scenario_generator import generate_scenario
from image_generator import generate_image

SUPPORTED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]


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
    try:
        scenario_data = generate_scenario(api_key=cfg["anthropic_api_key"])
    except Exception as e:
        print(f"Error generating scenario: {e}")
        sys.exit(1)

    print(f"\nScenario: {scenario_data['scenario']}\n")
    print("Generating image (this may take 20-40 seconds)...")

    try:
        output_path = generate_image(
            image_path=image_path,
            prompt=scenario_data["image_prompt"],
            scenario=scenario_data["scenario"],
        )
    except Exception as e:
        print(f"Error generating image: {e}")
        sys.exit(1)

    print(f"\nDone! Image saved to: {output_path}")


if __name__ == "__main__":
    run()
