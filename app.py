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

# st.sidebar.header("Settings")
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
#         st.sidebar.success("Document uploaded successfully!")
#         st.session_state["messages"].append({"role": "system", "content": f"Document content: {document_text}"})

# # Display previous messages in chat
# for message in st.session_state["messages"]:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # User input
# user_input = st.chat_input("Ask something...")
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

# User authentication (optional)
user = st.sidebar.text_input("Enter your username", key="username")

if not user:
    st.warning("Please enter a username to start chatting.")
    st.stop()

# Load user's chat history
user_chats = get_user_chats(user)
chat_options = ["Start New Chat"] + list(user_chats.keys())

# Select a chat from history or start a new one
selected_chat = st.sidebar.selectbox("Choose a chat:", chat_options)

# If starting a new chat, create a new chat ID
if selected_chat == "Start New Chat":
    chat_id = create_new_chat()
    st.session_state["messages"] = []  # Reset chat messages
else:
    chat_id = selected_chat
    st.session_state["messages"] = user_chats.get(chat_id, [])

st.title("📚 Together AI Chatbot 💬")

st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox("Choose AI Model", [
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    "meta-llama/Llama-Vision-Free",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
])
temperature = st.sidebar.slider("Creativity (Temperature)", 0.1, 1.0, 0.7)

uploaded_file = st.sidebar.file_uploader("📄 Upload PDF", type=["pdf"])

if uploaded_file:
    document_text = extract_text_from_pdf(uploaded_file)
    if document_text.startswith("Error"):
        st.sidebar.error(document_text)
    else:
        st.sidebar.success("✅ Document uploaded successfully!")
        st.session_state["messages"].append({"role": "system", "content": f"Document content: {document_text}"})

# Display previous messages in chat
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("💬 Ask something...")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # Call AI API with full chat context
    ai_response = call_together_ai(st.session_state["messages"], model_choice, temperature)

    st.session_state["messages"].append({"role": "assistant", "content": ai_response})

    # Save chat history
    save_chat_history(user, chat_id, st.session_state["messages"])

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown("## 📖 Maxwell's Equations")

        # Format response properly
        if "$$" in ai_response:
            equations = [eq.strip() for eq in ai_response.split("$$") if eq.strip()]
            for eq in equations:
                st.markdown(f'<p style="font-size:22px; font-weight:bold; text-align:center;">$$ {eq} $$</p>', unsafe_allow_html=True)
        else:
            # Ensure proper spacing and formatting
            formatted_response = ai_response.replace("\n", "\n\n")  # Add spacing for readability
            st.markdown(formatted_response, unsafe_allow_html=True)
