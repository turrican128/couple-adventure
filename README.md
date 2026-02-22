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
