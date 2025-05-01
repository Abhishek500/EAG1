import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("Assignment6.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
from perception import extract_perception
from memory import MemoryManager
from decision import generate_plan
from action import execute_tool, TOOLS # execute_tool is now async
import time
import asyncio # <-- Add asyncio




# Configure logging if not already done elsewhere
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Make main async
async def main() -> None:
    prefs = input("Tell me your preferences (likes, location, favorites): ")
    mem = MemoryManager()
    mem.store_item("preference", prefs)

    available_tools = ", ".join(TOOLS.keys())
    query = input("What can I help you with today? ")
    original_query = query # Keep the original query for context

    MAX_STEPS = 10 # Increased max steps for multi-step tasks
    steps = 0
    last_plan = None # To detect repeating the exact same function call

    # Initial perception
    p = extract_perception(original_query)
    # Store initial perception details if needed by planner later
    mem.store_item("initial_intent", p.intent)
    mem.store_item("initial_entities", p.entities)

    while steps < MAX_STEPS:
        logging.info(f"\n--- Step {steps + 1} ---")

        plan = generate_plan(p, mem.store, available_tools)

        # Handle the decision
        if plan.startswith("FINAL_ANSWER:"):
            answer = plan.split("FINAL_ANSWER:", 1)[1].strip(" []")
            print(f"🎯 Final answer: {answer}")
            break # Task complete

        elif plan.startswith("FUNCTION_CALL:"):
            tool_call_str = plan.split("FUNCTION_CALL:", 1)[1].strip()

            if "clarification_tool" in tool_call_str:
                print("⚠️ Clarification needed.")
                query = input("Could you please clarify your request? ")
                # Update perception based on new input
                p = extract_perception(query)
                mem.store_item("last_result", None) 
                mem.store_item("last_tool", None)
                last_plan = None
                steps += 1
                continue 

            if plan == last_plan:
                print("⚠️ Loop detected (same function call requested again) - Aborting.")
                logging.warning(f"Loop detected: Trying to call {plan} again immediately.")
                break

            # Execute the tool (now awaits async tools)
            logging.info(f"Executing Tool: {plan}")
            result = await execute_tool(plan) # <-- Use await
            print(f"⚙️ Result: {result}")
            logging.info(f"Tool Result: {result}")


            # Remember what happened for the *next* planning step
            mem.store_item("last_tool", plan)
            mem.store_item("last_result", result)
            # Optionally add to completed steps history
            completed = mem.recall_item("completed") or []
            completed.append(f"{plan} -> {result}")
            mem.store_item("completed", completed)

            last_plan = plan

            steps += 1
            await asyncio.sleep(0.5) 
            continue

        else:
            # Unexpected output from planner
            print(f"⚠️ Unexpected planner output: {plan}")
            logging.warning(f"Unexpected plan format: {plan}")
            break # Stop execution

    # After loop finishes
    if steps >= MAX_STEPS:
        print("⚠️ Maximum steps reached. Task may not be fully complete.")
        logging.warning("Maximum steps reached.")

# Run the async main function
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An error occurred in the main loop: {e}", exc_info=True)