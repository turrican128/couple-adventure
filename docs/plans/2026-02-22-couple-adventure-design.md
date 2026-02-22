# Couple Adventure Generator — Design Doc

**Date:** 2026-02-22

## Overview

A Python script that generates a new AI image of a real couple placed in a random creative scenario every time it is run. The couple's faces are preserved using fal.ai InstantID. Scenarios are generated fresh each run using the Claude API.

## Goals

- Run `python main.py` → get a new creative image of the real couple
- Face likeness preserved in every generated image
- Scenarios are always different and imaginative (bungee jumping, fancy restaurant, space, etc.)
- Simple setup: drop couple photo in `images/`, configure `.env`, run

## Architecture

```
couple-adventure/
├── images/              # Input: couple photo(s)
├── output/              # Output: timestamped generated images (git-ignored)
├── docs/plans/          # This design doc
├── main.py              # Entry point
├── scenario_generator.py
├── image_generator.py
├── .env                 # API keys (git-ignored)
├── .gitignore
├── requirements.txt
└── README.md
```

## Flow

1. `main.py` loads the couple image from `images/`
2. `scenario_generator.py` calls Claude API → returns `{ scenario, image_prompt }`
3. `image_generator.py` uploads image to fal.ai storage, calls `fal-ai/instant-id` with the prompt
4. Output image saved to `output/YYYY-MM-DD_HH-MM-SS.jpg`
5. Scenario description printed to console

## Components

### scenario_generator.py
- Calls `claude-opus-4-6` (or `claude-sonnet-4-6`) via Anthropic SDK
- System prompt instructs Claude to be wildly creative with unique couple scenarios
- Returns structured JSON: `scenario` (console description) + `image_prompt` (optimized for InstantID)

### image_generator.py
- Uploads couple image to fal.ai temporary storage
- Calls `fal-ai/instant-id` with image URL + prompt
- Downloads result and saves with timestamp

### main.py
- Thin orchestrator: load → generate scenario → generate image → save → print

## APIs & Dependencies

| Dependency     | Purpose                        |
|----------------|--------------------------------|
| `anthropic`    | Claude API for scenario gen    |
| `fal-client`   | fal.ai SDK for InstantID       |
| `python-dotenv`| Load API keys from `.env`      |
| `requests`     | Download generated image       |

## Environment Variables

```
ANTHROPIC_API_KEY=...
FAL_KEY=...
```

## Error Handling

- Missing image in `images/`: clear error message with instructions
- API failures: print error and exit with non-zero code (no silent failures)

## GitHub

- Repo: `couple-adventure`
- `.gitignore`: excludes `.env`, `output/`
- `images/` is tracked (couple photo lives in repo)
- README includes setup steps
