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

def format_math_content(text):
    """
    Enhance math equation formatting for better rendering.
    """
    # Format inline math
    text = re.sub(r'\$([^$]+)\$', r'\\(\1\\)', text)
    
    # Format block math
    text = re.sub(r'\$\$([^$]+)\$\$', r'\\[\1\\]', text)
    
    return text

def parse_thinking_response(response):
    """
    Separate thinking and response parts from the AI output.
    """
    thinking_pattern = r'<think>(.*?)</think>'
    thinking_match = re.search(thinking_pattern, response, re.DOTALL)
    
    if thinking_match:
        thinking = thinking_match.group(1).strip()
        response_text = re.sub(thinking_pattern, '', response, flags=re.DOTALL).strip()
    else:
        thinking = None
        response_text = response
    
    return thinking, response_text

def call_together_ai(messages, model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", temperature=0.7):
    """
    Enhanced API call with better formatting and math support.
    """
    try:
        # Add system message for math formatting if not present
        has_system_msg = any(msg["role"] == "system" for msg in messages)
        if not has_system_msg:
            messages.insert(0, {
                "role": "system",
                "content": "You are a helpful assistant. For mathematical equations, use LaTeX syntax with $ for inline math and $$ for display math. Format complex equations using display math for better readability. When thinking about a response, enclose your thoughts in <think> tags."
            })

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        
        if hasattr(response, "choices") and response.choices:
            raw_response = response.choices[0].message.content
            thinking, response_text = parse_thinking_response(raw_response)
            formatted_response = format_math_content(response_text)
            
            return {
                "thinking": thinking,
                "response": formatted_response
            }
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
    history[user][chat_id] = messages
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
    return str(uuid.uuid4())
