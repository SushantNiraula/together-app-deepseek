
import streamlit as st
# Load environment variables


# API Configuration
API_KEY = st.secrets["TOGETHER_API_KEY"]

# Debugging: Ensure API key is loaded
if not API_KEY:
    raise ValueError("API_KEY is missing. Check your .env file!")
