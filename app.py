# import streamlit as st
# from utils import (
#     call_together_ai, 
#     extract_text_from_pdf, 
#     save_chat_history, 
#     load_chat_history, 
#     get_user_chats, 
#     create_new_chat
# )

# # User authentication (optional)
# user = st.sidebar.text_input("Enter your username", key="username")

# if not user:
#     st.warning("Please enter a username to start chatting.")
#     st.stop()

# # Load user's chat history
# user_chats = get_user_chats(user)
# chat_options = ["Start New Chat"] + list(user_chats.keys())

# # Select a chat from history or start a new one
# selected_chat = st.sidebar.selectbox("Choose a chat:", chat_options)

# # If starting a new chat, create a new chat ID
# if selected_chat == "Start New Chat":
#     chat_id = create_new_chat()
#     st.session_state["messages"] = []  # Reset chat messages
# else:
#     chat_id = selected_chat
#     st.session_state["messages"] = user_chats.get(chat_id, [])

# st.title("Together AI Chatbot 💬")

# st.sidebar.header("⚙️ Settings")
# model_choice = st.sidebar.selectbox("Choose AI Model", [
#     "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
#     "meta-llama/Llama-Vision-Free",
#     "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
# ])
# temperature = st.sidebar.slider("Creativity (Temperature)", 0.1, 1.0, 0.7)

# uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

# if uploaded_file:
#     document_text = extract_text_from_pdf(uploaded_file)
#     if document_text.startswith("Error"):
#         st.sidebar.error(document_text)
#     else:
#         st.sidebar.success("✅ Document uploaded successfully!")
#         st.session_state["messages"].append({"role": "system", "content": f"Document content: {document_text}"})

# # Display previous messages in chat
# for message in st.session_state["messages"]:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # User input
# user_input = st.chat_input("💬 Ask something...")
# if user_input:
#     st.session_state["messages"].append({"role": "user", "content": user_input})

#     # Call API with full chat context
#     ai_response = call_together_ai(st.session_state["messages"], model_choice, temperature)

#     st.session_state["messages"].append({"role": "assistant", "content": ai_response})

#     # Save chat history
#     save_chat_history(user, chat_id, st.session_state["messages"])

#     with st.chat_message("assistant"):
#         st.markdown(ai_response)

import streamlit as st
from utils import (
    call_together_ai, 
    extract_text_from_pdf, 
    save_chat_history, 
    load_chat_history, 
    get_user_chats, 
    create_new_chat
)
import re

# Configure Streamlit page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Chat Message Styling */
    .stChatMessage {
        background-color: #f7f7f8;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    .stChatMessage [data-testid="chatAvatarIcon-user"] {
        background-color: #1a7f37;
    }
    
    .stChatMessage [data-testid="chatAvatarIcon-assistant"] {
        background-color: #0969da;
    }
    
    /* Equation Styling */
    .katex-display {
        margin: 1em 0;
        overflow-x: auto;
        overflow-y: hidden;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        padding: 2rem 1rem;
    }
    
    /* Input Box Styling */
    .stChatInputContainer {
        background-color: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin-top: 1rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #0969da;
        color: white;
        border: none;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        background-color: #0366d6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_title" not in st.session_state:
    st.session_state.chat_title = None

# Sidebar configuration
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=AI+Chat", use_column_width=True)
    st.title("⚙️ Chat Settings")
    
    # User authentication
    user = st.text_input("Username", key="username", placeholder="Enter your username")
    if not user:
        st.warning("⚠️ Please enter a username to start chatting.")
        st.stop()
    
    # Model selection
    st.subheader("🤖 AI Model")
    model_choice = st.selectbox(
        "Choose AI Model",
        [
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            "meta-llama/Llama-Vision-Free",
            "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        ]
    )
    
    # Advanced settings
    with st.expander("⚙️ Advanced Settings"):
        temperature = st.slider(
            "Creativity Level",
            min_value=0.1,
            max_value=1.0,
            value=0.7
        )
    
    # Document upload
    st.subheader("📄 Upload PDF")
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file:
        document_text = extract_text_from_pdf(uploaded_file)
        if document_text.startswith("Error"):
            st.error(document_text)
        else:
            st.success("✅ Document processed successfully!")
            st.write(f"**Document Preview:** {document_text[:500]}...")  # Show a short preview
            if len(st.session_state.messages) == 0:
                st.session_state.messages.append({
                    "role": "system",
                    "content": f"Context from uploaded document: {document_text[:1000]}..."
                })

# Main chat interface
st.title("💬 AI Chat Assistant")

# Chat history management
user_chats = get_user_chats(user)
chat_options = ["🆕 New Chat"] + list(user_chats.keys())
selected_chat = st.selectbox("💭 Select Conversation", chat_options)

if selected_chat == "🆕 New Chat":
    chat_id = create_new_chat()
    st.session_state.messages = []
else:
    chat_id = selected_chat
    if st.session_state.messages != user_chats.get(chat_id, []):
        st.session_state.messages = user_chats.get(chat_id, [])

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            content = message["content"]
            # Handle LaTeX equations properly
            content = content.replace("$$", "$")
            st.markdown(content)

# Chat input
user_input = st.chat_input("💬 Type your message here...")
if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Show AI "Thinking..." effect
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            ai_response = call_together_ai(
                st.session_state.messages,
                model_choice,
                temperature
            )
            
            # Add AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Format AI response
            ai_response = ai_response.replace("$$", "$")  # Ensure proper LaTeX display
            st.markdown(ai_response)
    
    # Save chat history
    save_chat_history(user, chat_id, st.session_state.messages)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>🚀 Built with Streamlit • Powered by Together AI</small>
    </div>
    """,
    unsafe_allow_html=True
)
