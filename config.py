import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("TOGETHER_API_KEY")

# Debugging: Ensure API key is loaded
if not API_KEY:
    raise ValueError("API_KEY is missing. Check your .env file!")
