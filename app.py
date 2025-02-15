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
import re
from utils import (
    call_together_ai, 
    extract_text_from_pdf, 
    save_chat_history, 
    load_chat_history, 
    get_user_chats, 
    create_new_chat
)

# Configure Streamlit page
st.set_page_config(
    page_title="AI Chat Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling and math rendering
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
    
    /* Math equations */
    .katex-display {
        background-color: #2D2E3A;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0 !important;
        border-left: 4px solid #10A37F;
    }
    
    .katex {
        font-size: 1.1em;
    }
    
    /* Thinking section */
    .thinking-section {
        background-color: #2A2B32;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #FFB454;
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        background-color: #444654;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid #2A2B32;
    }
    
    /* User messages */
    [data-testid="stChatMessage"][data-testid="user"] {
        background-color: #343541;
    }
    
    /* Input box */
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
    .sidebar .sidebar-content {
        background-color: #202123;
    }
    
    .stButton > button {
        background-color: #202123;
        color: #ECECF1;
        border: 1px solid #4A4B53;
        border-radius: 0.5rem;
        width: 100%;
        margin: 0.25rem 0;
    }
    
    .stButton > button:hover {
        background-color: #2A2B32;
    }
    
    .stSelectbox > div {
        background-color: #202123;
        color: #ECECF1;
        border: 1px solid #4A4B53;
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
    
    # Chat history
    st.subheader("💭 Conversations")
    user_chats = get_user_chats(user)
    
    if st.button("+ New Chat", key="new_chat"):
        st.session_state.current_chat = create_new_chat()
        st.session_state.messages = []
        st.experimental_rerun()
    
    for chat_id, messages in user_chats.items():
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
            if isinstance(message["content"], dict):
                # Display thinking part
                if message["content"].get("thinking"):
                    st.markdown(f"""
                        <div class="thinking-section">
                            💭 <i>{message["content"]["thinking"]}</i>
                        </div>
                    """, unsafe_allow_html=True)
                content = message["content"].get("response", "")
            else:
                content = message["content"]
            
            st.markdown(content)

# Chat input
if prompt := st.chat_input("Message AI..."):
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
            
            # Display thinking part
            if response.get("thinking"):
                st.markdown(f"""
                    <div class="thinking-section">
                        💭 <i>{response["thinking"]}</i>
                    </div>
                """, unsafe_allow_html=True)
            
            # Display main response
            st.markdown(response.get("response", ""))
    
    # Save chat history
    save_chat_history(user, st.session_state.current_chat, st.session_state.messages)
