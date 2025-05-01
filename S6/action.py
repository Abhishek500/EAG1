# action.py
import ast
from typing import Any, Callable, Dict
from PIL import Image as PILImage
import math, sys, time
from pywinauto.application import Application
import win32gui, win32con
import asyncio # <-- Add asyncio
import inspect # <-- Add inspect
import logging # Optional: for better debugging
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent

# --- Tool definitions (keep these as they are) ---

def add(a: int, b: int) -> int:
    return int(a + b)

def add_list(l: list) -> int:
    # Ensure list elements are numbers, handle potential errors
    try:
        return sum(float(x) for x in l)
    except (TypeError, ValueError):
        return "Error: List contains non-numeric elements"




def strings_to_chars_to_int(string: str) -> list[int]:
    " Converts a word into a list of its ASCII number"
    return [ord(c) for c in string]

def int_list_to_exponential_sum(int_list: list) -> float:
    " Reads a list of numbers , gets each number's exponential and then sums it up"
    try:
        # Ensure list elements are numbers
        numeric_list = [float(i) for i in int_list]
        return sum(math.exp(i) for i in numeric_list)
    except (TypeError, ValueError):
         return "Error: List contains non-numeric elements for exponential sum"
    except OverflowError:
         return "Error: Resulting exponential sum is too large to represent"


def fibonacci_numbers(n: int) -> list[int]:
    if n <= 0:
        return []
    seq = [0, 1]
    for _ in range(2, n): seq.append(seq[-1] + seq[-2])
    return seq[:n]


paint_app = None
async def open_paint() -> dict:
    """Open Microsoft Paint maximized on primary or secondary monitor."""
    global paint_app
    try:
        paint_app = Application().start('mspaint.exe')
        time.sleep(1.0)  # Let paint fully launch

        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Maximize the window
        win32gui.ShowWindow(paint_window.handle, win32con.SW_MAXIMIZE)
        time.sleep(1.0)

        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully and maximized."
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }


async def draw_rectangle(x1: int = 750, y1: int = 500, x2: int = 1100, y2: int= 650) -> dict:
    """
    Draw a rectangle in Paint from (x1,y1) to (x2,y2) using.
    Coordinates (x1,y1), (x2,y2) are assumed to be screen coordinates for drawing.
    x1  = 750, y1 = 500, x2 = 1100, y2 = 650
    """
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window and the canvas
        paint_window = paint_app.window(class_name='MSPaintApp')
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Ensure Paint window is active
        paint_window.set_focus()
        time.sleep(0.5)
        
        # Step 1: Click on the Rectangle tool in absolute screen coords
        paint_window.click_input(coords=(630, 92), absolute=True)

        time.sleep(0.5)
        

        # Step 2: Draw the rectangle on the canvas, using absolute screen coords.
        canvas.click_input(coords=(750,500))
        canvas.press_mouse_input(coords=(750,500))
        canvas.move_mouse_input(coords=(1100,650))
        canvas.release_mouse_input(coords=(1100,650))
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({750},{500}) to ({1100},{650})"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Ensure Paint window is active
        if not paint_window.has_focus():
            paint_window.set_focus()
            time.sleep(0.5)
        
        
        # Get the canvas area
        canvas = paint_window.child_window(class_name='MSPaintView')
        
        # Select text tool using keyboard shortcuts
        # paint_window.type_keys('t')
        # time.sleep(0.1)
        # paint_window.type_keys('x')
        # time.sleep(0.5)
        

        paint_window.click_input(coords=(412, 102), absolute=True)        
        
        # Click where to start typing
        canvas.click_input(coords=(810, 370))
        time.sleep(0.5)
        
        # Type the text passed from client
        paint_window.type_keys(text)
        time.sleep(0.5)
        
        # Click to exit text mode
        canvas.click_input(coords=(1050, 800))
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }



















###################
def clarification_tool() -> str:
    """Ask the user to clarify their request."""
    return "I’m not sure I understand—could you please clarify your request?"

# --- Registry (Ensure async functions are correctly referenced) ---
TOOLS: Dict[str, Callable[..., Any]] = {
    "add": add,
    "add_list": add_list,
    "strings_to_chars_to_int": strings_to_chars_to_int,
    "int_list_to_exponential_sum": int_list_to_exponential_sum,
    "fibonacci_numbers": fibonacci_numbers,
    "open_paint": open_paint,             # Reference async function
    "draw_rectangle": draw_rectangle,     # Reference async function
    "add_text_in_paint": add_text_in_paint, # Reference async function
    "clarification_tool": clarification_tool
}


# --- Make execute_tool async ---
async def execute_tool(call_str: str) -> Any:
    if not call_str.startswith("FUNCTION_CALL:"):
        # Maybe return an error message instead of raising?
        # Or let main handle the exception
        # raise ValueError("Not a FUNCTION_CALL string")
        return f"Error: Invalid tool call format '{call_str}'"

    _, body = call_str.split("FUNCTION_CALL:", 1)
    parts = [p.strip() for p in body.split("|")]
    name = parts[0]

    if name not in TOOLS:
        # raise ValueError(f"Unknown tool: {name}")
        return f"Error: Unknown tool '{name}'"

    func = TOOLS[name]

    # Prepare positional and keyword arguments
    args = []
    kwargs: Dict[str, Any] = {}
    for part in parts[1:]:
        if "=" in part:
            k, v = part.split("=", 1)
            try:
                # Safely evaluate literals, pass others as strings
                kwargs[k] = ast.literal_eval(v)
            except (ValueError, SyntaxError, TypeError):
                kwargs[k] = v # Keep as string if evaluation fails
        else:
            # no '=', treat as positional literal
            try:
                 # Safely evaluate literals, pass others as strings
                args.append(ast.literal_eval(part))
            except (ValueError, SyntaxError, TypeError):
                args.append(part) # Keep as string if evaluation fails

    # Call the function, awaiting if it's async
    try:
        if inspect.iscoroutinefunction(func):
            # print(f"Executing async tool: {name} with args={args}, kwargs={kwargs}")
            return await func(*args, **kwargs)
        else:
            # print(f"Executing sync tool: {name} with args={args}, kwargs={kwargs}")
            return func(*args, **kwargs)
    except Exception as e:
        # Catch errors during tool execution
        print(f"Error executing tool {name}: {e}")
        return f"Error during execution of {name}: {e}"