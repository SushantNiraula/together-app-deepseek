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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = create_new_chat()

# Sidebar
with st.sidebar:
    st.title("💬 AI Chat")
    user = st.text_input("Username", placeholder="Enter username", key="username")
    if not user:
        st.warning("Please enter a username")
        st.stop()
    
    st.divider()
    
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
                st.session_state.messages.append({
                    "role": "system",
                    "content": f"Context from document: {document_text[:1000]}..."
                })

# Main chat interface
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict):
                if message["content"].get("thinking"):
                    st.markdown(f"""
                        <div style='background-color:#2A2B32;padding:1rem;border-left:4px solid #FFB454;'>
                            💭 <i>{message["content"]["thinking"]}</i>
                        </div>
                    """, unsafe_allow_html=True)
                content = message["content"].get("response", "")
            else:
                content = message["content"]
            
            st.markdown(content)

# Chat input
if prompt := st.chat_input("Message AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = call_together_ai(
                st.session_state.messages,
                model_choice,
                temperature
            )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            if response.get("thinking"):
                st.markdown(f"""
                    <div style='background-color:#2A2B32;padding:1rem;border-left:4px solid #FFB454;'>
                        💭 <i>{response["thinking"]}</i>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(response.get("response", ""))
    
    save_chat_history(user, st.session_state.current_chat, st.session_state.messages)
