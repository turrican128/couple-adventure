import sys
from datetime import datetime
from pathlib import Path

from config import load_config
from scenario_generator import generate_scenario
from image_generator import generate_image

LOG_FILE = Path("output/generation_log.txt")


def append_log(scenario_data: dict, image_path: str, source_image: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"{'=' * 60}\n"
        f"Date & Time  : {timestamp}\n"
        f"Output Image : {image_path}\n"
        f"Source Photo : {source_image}\n"
        f"\nScenario:\n{scenario_data['scenario']}\n"
        f"\nImage Prompt:\n{scenario_data['image_prompt']}\n"
    )
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")

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

    append_log(scenario_data, output_path, image_path)
    print(f"\nDone! Image saved to: {output_path}")
    print(f"Log updated  : {LOG_FILE}")


if __name__ == "__main__":
    run()
