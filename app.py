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
import time

# Configure Streamlit page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like dark theme
st.markdown("""
<style>
    /* Global theme */
    [data-testid="stAppViewContainer"] {
        background-color: #343541;
        color: #ECECF1;
    }
    
    [data-testid="stSidebar"] {
        background-color: #202123;
        border-right: 1px solid #4A4B53;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ECECF1 !important;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #444654;
        border-radius: 0;
        border: none;
        padding: 1.5rem;
        margin: 0;
        border-bottom: 1px solid #2A2B32;
    }
    
    /* User messages */
    [data-testid="stChatMessage"][data-testid="user"] {
        background-color: #343541;
    }
    
    /* Message input box */
    .stChatInputContainer {
        background-color: #343541 !important;
        border-color: #4A4B53 !important;
        padding: 1rem !important;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 2rem !important;
    }
    
    .stChatInput {
        background-color: #40414F !important;
        border-color: #4A4B53 !important;
        color: #ECECF1 !important;
        border-radius: 0.5rem !important;
    }
    
    /* Sidebar elements */
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem;
    }
    
    .sidebar .sidebar-content {
        background-color: #202123;
    }
    
    /* Buttons and selectbox */
    .stButton > button {
        background-color: #202123;
        color: #ECECF1;
        border: 1px solid #4A4B53;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        width: 100%;
        margin: 0.25rem 0;
    }
    
    .stButton > button:hover {
        background-color: #2A2B32;
        border-color: #ECECF1;
    }
    
    .stSelectbox > div {
        background-color: #202123;
        color: #ECECF1;
        border: 1px solid #4A4B53;
        border-radius: 0.5rem;
    }
    
    /* Chat history buttons */
    .chat-button {
        background-color: transparent;
        color: #ECECF1;
        border: 1px solid #4A4B53;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.25rem 0;
        width: 100%;
        text-align: left;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .chat-button:hover {
        background-color: #2A2B32;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #202123;
        border-color: #4A4B53;
        color: #ECECF1;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #202123;
        color: #ECECF1;
        border-color: #4A4B53;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #202123;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4A4B53;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #ECECF1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# Sidebar
with st.sidebar:
    st.title("💬 AI Chat")
    
    # User authentication
    user = st.text_input("Username", placeholder="Enter username", key="username")
    if not user:
        st.warning("Please enter a username")
        st.stop()
    
    st.divider()
    
    # Chat history management
    st.subheader("💭 Conversations")
    user_chats = get_user_chats(user)
    
    # New chat button
    if st.button("+ New Chat", key="new_chat"):
        st.session_state.current_chat = create_new_chat()
        st.session_state.messages = []
        st.experimental_rerun()
    
    # Display existing chats
    for chat_id, messages in user_chats.items():
        # Get the first user message as chat title, or use default
        chat_title = next((msg["content"][:30] + "..." for msg in messages 
                          if msg["role"] == "user"), "New Conversation")
        if st.button(f"📄 {chat_title}", key=chat_id):
            st.session_state.current_chat = chat_id
            st.session_state.messages = messages
            st.experimental_rerun()
    
    st.divider()
    
    # Model settings
    st.subheader("⚙️ Settings")
    model_choice = st.selectbox(
        "Model",
        [
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
            "meta-llama/Llama-Vision-Free",
            "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
        ]
    )
    
    temperature = st.slider("Temperature", 0.1, 1.0, 0.7)
    
    # Document upload
    st.divider()
    st.subheader("📄 Upload Context")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        with st.spinner("Processing document..."):
            document_text = extract_text_from_pdf(uploaded_file)
            if document_text.startswith("Error"):
                st.error(document_text)
            else:
                st.success("Document processed!")
                if len(st.session_state.messages) == 0:
                    st.session_state.messages.append({
                        "role": "system",
                        "content": f"Context from document: {document_text[:1000]}..."
                    })

# Main chat interface
if not st.session_state.current_chat:
    st.session_state.current_chat = create_new_chat()

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Message DeepSeek..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_together_ai(
                st.session_state.messages,
                model_choice,
                temperature
            )
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(response)
    
    # Save chat history
    save_chat_history(user, st.session_state.current_chat, st.session_state.messages)
