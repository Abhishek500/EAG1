import logging
logger = logging.getLogger(__name__)
import os
import re
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')


class PerceptionResult(BaseModel):
    user_input: str
    intent: str
    entities: list[str]
    tool_hint: str | None = None


def extract_perception(user_input: str) -> PerceptionResult:
    """Use Gemini to extract intent, entities, and optional tool_hint."""
    prompt = f"""
You are an AI that extracts structured intent and entities from user text.

Input: "{user_input}"

Respond as a Python dict with keys:
- intent: a short phrase summarizing user goal
- entities: list of strings of extracted keywords
- tool_hint: optional tool name suggestion or null
Only output the dict on one line, no code fences.
"""

    logging.info(f"Calling Gemini with Perception module prompt : {prompt}")  # Log before API call

    resp = model.generate_content(
        contents=prompt
    ).text.strip()

    logging.info(f"Gemini response in Perception module: {resp}")  # Log after API call

    clean = re.sub(r"^```json|```$", "", resp, flags=re.MULTILINE).strip()
    # Replace JSON null with Python None
    clean = clean.replace("null", "None")
    data = eval(clean)
    entities = data.get("entities")
    if isinstance(entities, dict):
        entities = list(entities.values())
    return PerceptionResult(
        user_input=user_input,
        intent=data.get("intent", ""),
        entities=entities or [],
        tool_hint=data.get("tool_hint")
    )