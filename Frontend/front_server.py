import sys
from pathlib import Path
import tempfile
from typing import Optional
import requests
import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pipeline.agents import Voice_agent

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Voice Office Chatbot",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Chat container styling */
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* User message (right side, purple) */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-left: auto;
        max-width: 70%;
        width: fit-content;
        float: right;
        clear: both;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
    }
    
    /* Assistant message (left side, light gray) */
    .assistant-message {
        background-color: #1e2530;
        color: #e0e0e0;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        margin-right: auto;
        max-width: 70%;
        width: fit-content;
        float: left;
        clear: both;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        border: 1px solid #2d3748;
    }
    
    /* Error message styling */
    .error-message {
        background-color: #2d1f1f;
        color: #ff6b6b;
        padding: 15px 20px;
        border-radius: 18px;
        margin: 10px 0;
        border-left: 4px solid #ff6b6b;
    }
    
    /* Message icon */
    .message-icon {
        font-size: 1.2em;
        margin-right: 8px;
    }
    
    /* Clear floats */
    .clearfix::after {
        content: "";
        display: table;
        clear: both;
    }
    
    /* Input area at bottom */
    .input-section {
        position: sticky;
        bottom: 0;
        background-color: #0e1117;
        padding: 20px 0;
        border-top: 1px solid #2d3748;
        margin-top: 30px;
    }
    
    /* Recorder container */
    .recorder-container {
        background-color: #1e2530;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3748;
    }
    
    /* Custom button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        color: #ffffff;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_query" not in st.session_state:
    st.session_state.current_query = None
if "temp_file_path" not in st.session_state:
    st.session_state.temp_file_path = None

# -------------------- HELPER FUNCTIONS --------------------
def cleanup_temp_file():
    """Clean up temporary audio file"""
    if st.session_state.temp_file_path and Path(st.session_state.temp_file_path).exists():
        try:
            Path(st.session_state.temp_file_path).unlink()
        except Exception:
            pass  # Silently fail if already deleted
        st.session_state.temp_file_path = None

def send_query_to_server(query: str) -> dict:
    """Send query to backend and return response with status"""
    try:
        response = requests.post(
            "http://127.0.0.1:8000/server",
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()

        return {
            "success": True,
            "content": response.json().get("response", "No response received")
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "content": "❌ Server Error: Cannot connect to server. Please ensure the server is running on http://127.0.0.1:8000"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "content": "⏱️ Timeout Error: Server took too long to respond. Please try again."
        }
    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "content": f"❌ HTTP Error: {e.response.status_code} - {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "content": f"❌ Unexpected Error: {str(e)}"
        }

def render_message(message: dict):
    """Render a single message with appropriate styling"""
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        st.markdown(f"""
        <div class="clearfix">
            <div class="user-message">
                <span class="message-icon">👤</span>{content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:  # assistant
        # Check if it's an error message
        if content.startswith("❌") or content.startswith("⏱️"):
            st.markdown(f"""
            <div class="clearfix">
                <div class="error-message">
                    {content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="clearfix">
                <div class="assistant-message">
                    <span class="message-icon">🤖</span>{content}
                </div>
            </div>
            """, unsafe_allow_html=True)

# -------------------- MAIN UI --------------------
# Header
st.markdown('<h1 class="main-title">🎙️ Voice Office Chatbot</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Speak your query and get instant AI-powered responses</p>', unsafe_allow_html=True)

# Chat messages container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if not st.session_state.messages:
    # Welcome message when chat is empty
    st.markdown("""
    <div class="clearfix">
        <div class="assistant-message">
            <span class="message-icon">🤖</span>
            Hello! I'm your Voice Office Assistant. Click the microphone button below to record your question, and I'll help you out! 👋
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render all messages
    for message in st.session_state.messages:
        render_message(message)

st.markdown('</div>', unsafe_allow_html=True)

# Add some spacing before input
st.markdown("<br>" * 2, unsafe_allow_html=True)

# -------------------- INPUT SECTION (BOTTOM) --------------------
st.markdown('<div class="input-section">', unsafe_allow_html=True)

# Voice recorder in a styled container
st.markdown('<div class="recorder-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    audio = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="⏹️ Stop Recording",
        key="voice_recorder",
        use_container_width=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# Process audio when recorded
if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio["bytes"])
        st.session_state.temp_file_path = f.name
    
    with st.spinner("🎧 Transcribing your voice..."):
        try:
            query = Voice_agent(st.session_state.temp_file_path)
            st.session_state.current_query = query
            st.success(f"✅ Transcribed: **{query}**")
        except Exception as e:
            st.error(f"❌ Error processing audio: {str(e)}")
            st.session_state.current_query = None
        finally:
            cleanup_temp_file()

# Send button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    send_disabled = st.session_state.current_query is None
    
    if st.button(
        "📤 Send Query" if st.session_state.current_query else "🎙️ Record First",
        type="primary",
        disabled=send_disabled,
        use_container_width=True
    ):
        if st.session_state.current_query:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": st.session_state.current_query
            })
            
            # Get response from server
            with st.spinner("🤔 Processing your query..."):
                response = send_query_to_server(st.session_state.current_query)
            
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["content"]
            })
            
            # Clear current query
            st.session_state.current_query = None
            
            # Rerun to update UI
            st.rerun()

# Bottom controls
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_query = None
        st.rerun()

with col3:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

