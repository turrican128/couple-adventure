import json
import re
from anthropic import Anthropic

SYSTEM_PROMPT = """You are a wildly creative director for a couple's adventure photo series.
Your job is to invent unique, vivid, and visually striking scenarios where a real couple is placed.
Think big: exotic locations, extraordinary activities, fantasy settings, historical moments, or absurd fun.
Each scenario must be visually distinctive and feel like a real photograph moment."""

USER_PROMPT = """Generate a completely random and creative scenario for a couple's adventure photo.

Return ONLY a valid JSON object with this exact structure (no other text):
{
  "scenario": "A short 1-2 sentence description of the scenario for display",
  "image_prompt": "A detailed photorealistic image generation prompt. Start with 'A couple' and describe what they are doing, the setting, lighting, atmosphere, camera angle, and visual style. Be specific and vivid. Aim for 3-5 sentences."
}"""


def generate_scenario(api_key: str) -> dict:
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Claude response as JSON: {e}\nResponse was: {raw}")

    for field in ("scenario", "image_prompt"):
        if field not in data:
            raise ValueError(f"Claude response missing required field '{field}'. Got: {data}")

    return data
