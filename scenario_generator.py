import json
import random
import re
from anthropic import Anthropic

POSES = [
    "kissing passionately",
    "running and laughing together",
    "one lifting the other in the air",
    "hugging tightly from behind",
    "holding hands and looking at each other",
    "mid-jump with arms spread wide",
    "one dipping the other in a dance move",
    "sitting close together, leaning in",
    "back to back, arms crossed, looking away dramatically",
    "walking together, caught mid-stride",
    "one pointing into the distance while the other looks",
    "both looking up in awe at something above them",
]

CATEGORIES = [
    "Outer space / sci-fi — astronauts on Mars, alien planet surface, inside a space station, floating in a nebula",
    "Historical eras — ancient Rome colosseum, medieval jousting tournament, 1920s speakeasy jazz club, Egyptian pyramid construction, samurai Japan cherry blossom",
    "Extreme sports — tandem skydiving over Grand Canyon, surfing a massive wave in Hawaii, bungee jumping off a cliff, Formula 1 pit lane, white-water rafting",
    "Fantasy / magical — riding a dragon over a volcano, floating sky islands at sunset, inside a wizard's tower, enchanted forest with fairies, giant mushroom kingdom",
    "Famous landmarks — top of Eiffel Tower at night with fireworks, inside the Roman Colosseum, Great Wall of China at sunrise, Machu Picchu in the clouds, Taj Mahal at golden hour",
    "Absurd / funny — riding a giant rubber duck in a bathtub city, falling into a massive birthday cake, flying on a magic carpet over a busy city, inside a giant snow globe, shrunk to the size of ants in a garden",
    "Luxury / glamour — black-tie gala on a Monaco superyacht, rooftop dinner above the Tokyo skyline, private jet over the Alps, Venice gondola under fireworks, champagne tower at a Parisian penthouse",
    "Nature extremes — standing on the edge of an erupting volcano, watching the Northern Lights in Lapland, inside the eye of a tornado, summit of Mount Everest at sunrise, deep in the Amazon rainforest",
    "Pop culture / retro — inside a giant comic book panel, neon-lit cyberpunk Tokyo street, Wild West saloon showdown, aboard a pirate ship in a storm, 1980s neon roller disco",
    "Underwater world — coral reef fine dining restaurant, inside a glass submarine, ancient sunken city of Atlantis, whale swimming alongside them, deep sea bioluminescent trench",
]

SYSTEM_PROMPT = """You are a wildly creative director for a couple's adventure photo series.
Your job is to invent a specific, vivid, and visually striking scenario within the given category.
The scenario must feel like a real photograph moment — cinematic, detailed, and surprising."""

USER_PROMPT_TEMPLATE = """Generate a creative scenario for a couple's adventure photo in this exact category:

CATEGORY: {category}
POSE: The couple must be {pose} — incorporate this naturally into the scene.

Invent something specific and visually striking within this category. Do not stray into other categories.

Return ONLY a valid JSON object with this exact structure (no other text):
{{
  "scenario": "A short 1-2 sentence description of the scenario for display",
  "image_prompt": "An image EDITING instruction for FLUX Kontext. The instruction transforms the couple's existing photo into a new adventure scene. Start with 'Transform this photo:' then describe the new setting, pose ({pose}), lighting, atmosphere and visual style in vivid detail. End with 'Keep the two people\\'s faces, hair and appearance exactly as they are in the original photo.' Be specific and cinematic. Aim for 3-5 sentences."
}}"""


def generate_scenario(api_key: str) -> dict:
    category = random.choice(CATEGORIES)
    pose = random.choice(POSES)
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT_TEMPLATE.format(category=category, pose=pose)}],
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
