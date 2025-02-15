from together import Together
import fitz  # PyMuPDF for PDF handling
import json
import os
import re
from config import API_KEY

# Initialize Together AI client
client = Together(api_key=API_KEY)

CHAT_HISTORY_FILE = "chat_history.json"

def call_together_ai(messages, model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", temperature=0.7):
    """
    Sends a request to the Together AI API and returns the response.
    Formats the output to separate <think> reasoning and equations properly.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

        if hasattr(response, "choices") and response.choices:
            formatted_think, formatted_answer = format_response(response.choices[0].message.content)
            return formatted_think, formatted_answer
        else:
            return "Error: Unexpected response format from API.", ""

    except Exception as err:
        return f"An unexpected error occurred: {err}", ""

def extract_text_from_pdf(file):
    """
    Extract text from an uploaded PDF file using PyMuPDF (fitz).
    """
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "\n\n".join(page.get_text("text") for page in doc)
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def load_chat_history():
    """
    Load chat history from a JSON file.
    Handles empty or corrupted files gracefully.
    """
    if os.path.exists(CHAT_HISTORY_FILE):
        try:
            with open(CHAT_HISTORY_FILE, "r") as file:
                data = file.read()
                return json.loads(data) if data else {}
        except json.JSONDecodeError:
            return {}
    return {}

def save_chat_history(user, chat_id, messages):
    """
    Save chat history to a JSON file.
    """
    history = load_chat_history()

    if user not in history:
        history[user] = {}

    history[user][chat_id] = messages  # Store chat under a unique ID

    with open(CHAT_HISTORY_FILE, "w") as file:
        json.dump(history, file, indent=4)

def get_user_chats(user):
    """
    Get all chat IDs and summaries for a user.
    """
    history = load_chat_history()
    return history.get(user, {})

def create_new_chat():
    """
    Generate a new chat ID.
    """
    import uuid
    return str(uuid.uuid4())  # Unique chat identifier

def format_response(response):
    """
    Formats response to:
    1. Separate <think> ... </think> reasoning from final answer.
    2. Render equations in proper LaTeX format.
    """
    # Separate <think> section
    think_match = re.search(r"<think>(.*?)</think>", response, re.DOTALL)
    think_section = think_match.group(1).strip() if think_match else "No reasoning provided."

    # Remove <think> from the main answer
    formatted_answer = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL).strip()

    # Ensure proper LaTeX formatting for block equations
    formatted_answer = re.sub(r'\[([^\]]+)\]', r'$$\1$$', formatted_answer)  # Convert [ ... ] to $$ ... $$

    return think_section, formatted_answer
