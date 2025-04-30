# Gemini Powered Multi-Tool Agent 🚀

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project demonstrates an AI agent powered by Google's Gemini model. The agent can understand natural language requests, break them down into sequential steps, and execute those steps using a predefined set of tools. Notably, it includes tools for performing calculations and **automating the UI of Microsoft Paint** on Windows using `pywinauto`.

The agent follows a **Perceive-Plan-Act** cycle:
1.  **Perceive:** Understands the user's request using Gemini to extract intent and entities.
2.  **Plan:** Determines the next best action (which tool to call with what arguments) using Gemini, considering the goal, available tools, and past actions/results.
3.  **Act:** Executes the chosen tool, which might be a simple calculation or a complex UI automation task like opening Paint, drawing shapes, and adding text.

---

## ✨ Features

*   **Natural Language Understanding:** Leverages Gemini (`gemini-2.0-flash`) for intent/entity extraction.
*   **Multi-step Planning & Execution:** Breaks down complex tasks into sequential tool calls.
*   **Extensible Tool Library (`action.py`):** Includes tools for:
    *   Mathematical operations (add, subtract, power, sqrt, log, etc.)
    *   String/List manipulations (ASCII conversion, exponential sum)
    *   **MS Paint UI Automation (Windows Only):**
        *   Opening Paint (`open_paint`)
        *   Drawing rectangles (`draw_rectangle`)
        *   Adding text (`add_text_in_paint`)
*   **Asynchronous Operations:** Handles potentially long-running UI tasks using `asyncio`.
*   **Basic Memory:** Remembers the last action and result to inform planning (`memory.py`).
*   **Modular Code:** Separated components for perception, decision, action, and memory.

---

## 🖼️ Demo

*(Consider adding the screenshot you provided earlier here, showing the terminal output for the "INDIA" -> Paint task)*



*(Replace the placeholder screenshot comment above with actual Markdown image link: `![Agent Demo Screenshot](path/to/your/screenshot.png)`)*

---

## 🛠️ Tech Stack

*   **Python 3.9+**
*   **Google Generative AI SDK (`google-generativeai`)**: For interacting with the Gemini API.
*   **PyWinAuto**: For Windows GUI automation (controlling MS Paint).
*   **Pillow (PIL Fork)**: Used by some tools (e.g., if image processing were added).
*   **Python-Dotenv**: For managing environment variables (API keys).

---

## 📁 Project Structure
├── main.py # Main execution script, orchestrates the agent loop
├── perception.py # Handles understanding user input via Gemini
├── decision.py # Handles planning the next action via Gemini
├── action.py # Defines and executes available tools (math, Paint UI, etc.)
├── memory.py # Simple memory management class
├── requirements.txt # Python package dependencies
├── .env # Environment variables (Gitignored)
└── README.md # This file




---

## ⚙️ Setup

1.  **Prerequisites:**
    *   Python 3.9 or higher.
    *   **Windows Operating System** (required for `pywinauto` and MS Paint automation).
    *   Microsoft Paint installed.

2.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```

3.  **Set up a Virtual Environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
    ```bash
    # macOS/Linux (Note: Paint tools won't work)
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You'll need to create this `requirements.txt` file based on your imports. See below)*

5.  **Configure API Key:**
    *   Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create a file named `.env` in the project root directory.
    *   Add your API key to the `.env` file:
        ```dotenv
        GEMINI_API_KEY=YOUR_API_KEY_HERE
        ```
    *   **Important:** Ensure `.env` is listed in your `.gitignore` file to avoid committing your key.

---

## ▶️ Usage

Run the main script from your terminal:

```bash
python main.py
```

The script will first ask for your preferences (this is currently just stored in memory but could be used by the planner) and then prompt you for what you want the agent to do.
Example Input:
Convert letters of INDIA to ASCII numbers, get their exponentials, and then sum them. Open Paint, draw a rectangle on it, add text and paste the final sum there
The agent will then proceed through the perceive-plan-act cycle, printing tool calls and results, potentially opening and manipulating MS Paint on your screen.
🧠 How It Works
Input: main.py takes user input.
Perception: perception.py sends the input to Gemini to get structured intent and entities.
Decision: decision.py sends the perception results, available tools, and memory (last_result) to Gemini, asking it to choose the next FUNCTION_CALL or provide a FINAL_ANSWER.
Action: action.py parses the FUNCTION_CALL, finds the corresponding tool function (which could be sync or async), executes it with the provided arguments, and returns the result. main.py uses asyncio.run and await to handle async tool calls correctly.
Memory Update: main.py stores the last_tool called and its last_result in the MemoryManager.
Loop: The process repeats from Step 3 (Decision) until Gemini provides a FINAL_ANSWER or the maximum step count is reached.
🔧 Tooling Details
The available tools are defined in action.py and registered in the TOOLS dictionary. The decision-making prompt in decision.py makes the LLM aware of these tools.
The MS Paint tools (open_paint, draw_rectangle, add_text_in_paint) use pywinauto to interact with the Paint application window. They rely on:
Starting/Connecting to the mspaint.exe process.
Finding UI elements (like the main window and canvas) often by class_name.
Simulating mouse clicks (click_input, press_mouse_input, etc.) and keyboard input (type_keys).
Hardcoded Coordinates: Some actions (like clicking specific toolbar buttons) use absolute screen coordinates defined within the functions.
