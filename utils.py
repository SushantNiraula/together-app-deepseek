# from together import Together
# import fitz  # PyMuPDF for PDF handling
# import json
# import os
# from config import API_KEY

# # Initialize Together AI client
# client = Together(api_key=API_KEY)

# CHAT_HISTORY_FILE = "chat_history.json"

# def call_together_ai(messages, model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", temperature=0.7):
#     """
#     Sends a request to the Together AI API and returns the response.
#     Ensures conversation context is maintained.
#     """
#     try:
#         response = client.chat.completions.create(
#             model=model,
#             messages=messages,
#             temperature=temperature
#         )

#         if hasattr(response, "choices") and response.choices:
#             return response.choices[0].message.content
#         else:
#             return "Error: Unexpected response format from API."

#     except Exception as err:
#         return f"An unexpected error occurred: {err}"

# def extract_text_from_pdf(file):
#     """
#     Extract text from an uploaded PDF file using PyMuPDF (fitz).
#     """
#     try:
#         doc = fitz.open(stream=file.read(), filetype="pdf")
#         text = "\n\n".join(page.get_text("text") for page in doc)
#         return text
#     except Exception as e:
#         return f"Error extracting text from PDF: {str(e)}"

# def load_chat_history():
#     """
#     Load chat history from a JSON file.
#     Handles empty or corrupted files gracefully.
#     """
#     if os.path.exists(CHAT_HISTORY_FILE):
#         try:
#             with open(CHAT_HISTORY_FILE, "r") as file:
#                 data = file.read()
#                 return json.loads(data) if data else {}
#         except json.JSONDecodeError:
#             return {}
#     return {}

# def save_chat_history(user, chat_id, messages):
#     """
#     Save chat history to a JSON file.
#     """
#     history = load_chat_history()

#     if user not in history:
#         history[user] = {}

#     history[user][chat_id] = messages  # Store chat under a unique ID

#     with open(CHAT_HISTORY_FILE, "w") as file:
#         json.dump(history, file, indent=4)

# def get_user_chats(user):
#     """
#     Get all chat IDs and summaries for a user.
#     """
#     history = load_chat_history()
#     return history.get(user, {})

# def create_new_chat():
#     """
#     Generate a new chat ID.
#     """
#     import uuid
#     return str(uuid.uuid4())  # Unique chat identifier



from together import Together
import fitz  # PyMuPDF for PDF handling
import json
import os
import re
from config import API_KEY

# Initialize Together AI client
client = Together(api_key=API_KEY)
CHAT_HISTORY_FILE = "chat_history.json"

def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file."""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            text = "\n".join(page.get_text("text") for page in doc)
        return text if text else "Error: No text found in the document."
    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def format_response_with_thinking(response_text):
    """
    Parse thinking and response from the AI output and format as a dictionary.
    """
    thinking_pattern = r'<think>(.*?)</think>'
    thinking_match = re.search(thinking_pattern, response_text, re.DOTALL)
    
    if thinking_match:
        thinking = thinking_match.group(1).strip()
        response = re.sub(thinking_pattern, '', response_text, flags=re.DOTALL).strip()
    else:
        thinking = None
        response = response_text
    
    return {
        "thinking": thinking,
        "response": response
    }

def call_together_ai(messages, model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", temperature=0.7):
    """
    Make an API call to Together AI and return a formatted response.
    """
    try:
        # Convert any dictionary messages to strings for API
        api_messages = []
        for msg in messages:
            if isinstance(msg["content"], dict):
                content = msg["content"].get("response", "")
            else:
                content = msg["content"]
            api_messages.append({"role": msg["role"], "content": content})

        # Add system message for better formatting
        if not any(msg["role"] == "system" for msg in api_messages):
            api_messages.insert(0, {
                "role": "system",
                "content": "You are a helpful assistant. When thinking about a response, enclose your thoughts in <think> tags. For mathematical equations, use LaTeX syntax with $ for inline math and $$ for display math."
            })

        response = client.chat.completions.create(
            model=model,
            messages=api_messages,
            temperature=temperature
        )
        
        if hasattr(response, "choices") and response.choices:
            raw_response = response.choices[0].message.content
            return format_response_with_thinking(raw_response)
        else:
            return {
                "thinking": None,
                "response": "Error: Unexpected response format from API."
            }
    except Exception as err:
        return {
            "thinking": None,
            "response": f"An unexpected error occurred: {err}"
        }

def save_chat_history(username, chat_id, messages):
    """
    Save chat history to a file.
    """
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
        else:
            chat_data = {}

        if username not in chat_data:
            chat_data[username] = {}

        chat_data[username][chat_id] = messages

        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=4)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def load_chat_history(username, chat_id):
    """
    Load chat history from a file.
    """
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            return chat_data.get(username, {}).get(chat_id, [])
        return []
    except Exception as e:
        print(f"Error loading chat history: {e}")
        return []

def get_user_chats(username):
    """
    Retrieve a list of chat histories for a given user.
    """
    try:
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            return chat_data.get(username, {})
        return {}
    except Exception as e:
        print(f"Error retrieving user chats: {e}")
        return {}

import time  # Add this import at the top

def create_new_chat():
    """Generate a new unique chat ID."""
    return f"chat_{int(time.time())}"
