import sys
from datetime import datetime
from pathlib import Path

from config import load_config
from scenario_generator import generate_scenario
from image_generator import generate_image

def write_log(scenario_data: dict, image_path: str, source_image: str):
    log_path = Path(image_path).with_suffix(".txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"Date & Time  : {timestamp}\n"
        f"Output Image : {image_path}\n"
        f"Source Photo : {source_image}\n"
        f"\nScenario:\n{scenario_data['scenario']}\n"
        f"\nImage Prompt:\n{scenario_data['image_prompt']}\n"
    )
    log_path.write_text(entry, encoding="utf-8")

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


def run(count: int = 1):
    print("Couple Adventure Generator")
    print("-" * 40)

    cfg = load_config()
    image_path = get_couple_image_path()
    print(f"Using image: {image_path}")

    for i in range(count):
        if count > 1:
            print(f"\n[{i + 1}/{count}] Generating scenario...")
        else:
            print("Generating scenario...")

        try:
            scenario_data = generate_scenario(api_key=cfg["anthropic_api_key"])
        except Exception as e:
            print(f"Error generating scenario: {e}")
            sys.exit(1)

        print(f"Scenario: {scenario_data['scenario']}\n")
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

        write_log(scenario_data, output_path, image_path)
        log_path = Path(output_path).with_suffix(".txt")
        print(f"Done! Image saved to: {output_path}")
        print(f"Log saved    : {log_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Couple Adventure Generator")
    parser.add_argument("--count", type=int, default=1, help="Number of images to generate")
    args = parser.parse_args()
    run(count=args.count)
