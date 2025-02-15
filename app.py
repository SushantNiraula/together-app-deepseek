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
    
    /* Math rendering */
    .math-block {
        background-color: #2D2E3A;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-size: 1.1em;
        border-left: 4px solid #10A37F;
    }
    
    .math-inline {
        background-color: #2D2E3A;
        padding: 0.2rem 0.4rem;
        border-radius: 0.3rem;
        margin: 0 0.2rem;
    }
    
    /* Thinking section */
    .thinking-block {
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
    
    /* Rest of the CSS remains the same as before */
    /* ... (previous CSS) ... */
</style>

<!-- Add MathJax for better equation rendering -->
<script type="text/javascript">
window.MathJax = {
    tex: {
        inlineMath: [['\\(', '\\)']],
        displayMath: [['\\[', '\\]']],
        processEscapes: true,
        processEnvironments: true
    },
    options: {
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
    }
};
</script>
<script type="text/javascript" id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

# Sidebar configuration
with st.sidebar:
    # ... (previous sidebar code remains the same) ...
    pass

# Main chat interface
if not st.session_state.current_chat:
    st.session_state.current_chat = create_new_chat()

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict):
                # Display thinking part if it exists
                if message["content"].get("thinking"):
                    st.markdown(f"""
                        <div class="thinking-block">
                            💭 <i>{message["content"]["thinking"]}</i>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Display main response with enhanced math
                content = message["content"]["response"]
            else:
                content = message["content"]
            
            # Wrap display math in special div
            content = re.sub(
                r'\\\\[\s\S]+?\\\\]',
                lambda m: f'<div class="math-block">{m.group()}</div>',
                content
            )
            
            # Wrap inline math in special span
            content = re.sub(
                r'\\\\(.+?)\\\\)',
                lambda m: f'<span class="math-inline">{m.group()}</span>',
                content
            )
            
            st.markdown(content, unsafe_allow_html=True)

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
                st.session_state.get("model_choice", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"),
                st.session_state.get("temperature", 0.7)
            )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display thinking part if it exists
            if response.get("thinking"):
                st.markdown(f"""
                    <div class="thinking-block">
                        💭 <i>{response["thinking"]}</i>
                    </div>
                """, unsafe_allow_html=True)
            
            # Display main response
            st.markdown(response["response"], unsafe_allow_html=True)
    
    # Save chat history
    save_chat_history(
        st.session_state.get("username", "default_user"),
        st.session_state.current_chat,
        st.session_state.messages
    )
