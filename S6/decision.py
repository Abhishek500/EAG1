import logging
logger = logging.getLogger(__name__)
import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv
from perception import PerceptionResult

# ──────────────────────────── logging & model setup ─────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

dotenv_path = os.getenv("DOTENV_PATH", ".env")
load_dotenv(dotenv_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

# used in the prompt to discourage repeating identical calls
DEF_LOOP_GUARD = (
    "DO NOT call the same tool again with identical arguments."
)

# ──────────────────────────── planner / decision logic ──────────────────────

def generate_plan(
    perception: PerceptionResult,
    memory_store: dict[str, object],
    tool_descriptions: Optional[str] = None,
) -> str:
    """Return exactly one line:
        FUNCTION_CALL:<tool>|arg1|arg2|...
      or FINAL_ANSWER:[answer]
    """

    pref = memory_store.get("preference")
    last_result = memory_store.get("last_result")
    completed_steps = memory_store.get("completed", [])

    # ── build dynamic prompt ────────────────────────────────────────────────
    parts: list[str] = [
        "System: You are an AI agent that can think step‑by‑step and call tools to accomplish the user's goal.",
    ]
    if pref:
        parts.append(f"User preferences: {pref}")
    if tool_descriptions:
        parts.append(f"Available tools:\n{tool_descriptions}")
    if completed_steps:
        parts.append(f"Steps already completed: {', '.join(completed_steps)}")
    if last_result is not None:
        parts.append(f"Latest tool result: {last_result}\n{DEF_LOOP_GUARD}")

    parts.append(
        f"\nUser instruction: \"{perception.user_input}\"\n"
        f"Intent: {perception.intent}\n"
        f"Entities: {perception.entities}"
    )

    parts.append(
        """
**Guidelines**
1. If another tool is required to progress toward the user's goal, respond with:
   FUNCTION_CALL: <tool>|arg1|arg2|...
2. When the task is fully complete, respond with:
   FINAL_ANSWER: [your answer]
3. If unclear or no tool fits, respond with:
   FUNCTION_CALL: clarification_tool
Respond with **exactly one line**, no extra commentary.
"""
    )

    prompt = "\n\n".join(parts)

    # ── call model ─────────────────────────────────────────────────────────
    logging.info("Calling Gemini with Decision module prompt: %s", prompt)
    response = model.generate_content(contents=prompt).text.strip()
    logging.info("Gemini response for Decision module: %s", response)

    # ── return first valid directive line ───────────────────────────────────
    for line in response.splitlines():
        if line.startswith(("FUNCTION_CALL:", "FINAL_ANSWER:")):
            return line.strip()

    # fallback safeguard: ask for clarification
    return "FUNCTION_CALL: clarification_tool"
