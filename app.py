import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import PyPDF2
import docx

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Function to call Groq AI with chat history
def get_response(messages):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Error: " + str(e)

def get_streaming_response(messages):
    try:
        with client.chat.completions.stream(
            model="llama-3.3-70b-versatile",
            messages=messages
        ) as stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
    except Exception as e:
        yield "Error: " + str(e)

# Page config
st.set_page_config(page_title="AI Study Assistant", page_icon="🧠", layout="wide")

# Custom CSS injection for premium frontend styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp, .stMarkdown, .stText, h1, h2, h3, h4, h5, h6, p, label, .stButton button, .stDownloadButton button {
        font-family: 'Inter', sans-serif !important;
    }

    /* Main container styling */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1000px;
    }
    
    /* Elegant gradient title */
    h1 {
        font-weight: 800;
        background: linear-gradient(135deg, #FF4B4B, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }

    /* Standard Button Styling */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 65px;
        font-weight: 600;
        border: 1px solid rgba(255, 75, 75, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(255, 75, 75, 0.15);
    }
    
    /* Subheaders */
    h3 {
        font-weight: 600 !important;
        padding-bottom: 0.5rem;
    }

    /* File uploader hover */
    [data-testid="stFileUploadDropzone"] {
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #FF4B4B;
        background-color: rgba(255, 75, 75, 0.05);
    }
</style>
""", unsafe_allow_html=True)

st.title("AI Study Assistant 🧠")
st.caption("Your intelligent, context-aware companion for summarizing, explaining, and studying.")

# Session state for notes and chat
if "user_notes" not in st.session_state:
    st.session_state.user_notes = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Input / Notes Configuration
with st.sidebar:
    st.header("📝 Source Material")
    st.markdown("Upload a document or paste your notes to get started.")
    
    uploaded_file = st.file_uploader("Upload Notes (txt, pdf, docx)", type=["txt", "pdf", "docx"])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1].lower()
    
        # TXT
        if file_type == "txt":
            st.session_state.user_notes = uploaded_file.read().decode("utf-8")
    
        # PDF
        elif file_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            st.session_state.user_notes = text
    
        # DOCX
        elif file_type == "docx":
            doc = docx.Document(uploaded_file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            st.session_state.user_notes = text
    
        st.success("Document loaded successfully ✅")
        st.caption(f"📊 Document Size: {len(st.session_state.user_notes.split())} words")
        
        with st.expander("📄 View Source Content"):
            st.text_area("", st.session_state.user_notes, height=250, disabled=True)
            
    else:
        st.session_state.user_notes = st.text_area("Or paste your notes directly:", height=300, placeholder="Paste your text here...")

    if st.session_state.messages:
        st.divider()
        if st.button("🗑️ Clear Chat History", help="Reset the chat and wipe history"):
            st.session_state.messages = []
            st.rerun()
            
        full_chat = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📥 Export Chat Log", data=full_chat, file_name="chat_history.txt", mime="text/plain", use_container_width=True)

# Main Content Area
st.divider()

# Quick action buttons in columns
st.subheader("⚡ Quick Actions")
col1, col2, col3, col4 = st.columns(4)

if col1.button("📄 Summarize"):
    if st.session_state.user_notes.strip():
        prompt = "Summarize these notes clearly and concisely:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Summarizing..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please provide source material in the sidebar first!")

if col2.button("🔵 Bullet Points"):
    if st.session_state.user_notes.strip():
        prompt = "Convert these notes into clear bullet points:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Creating bullet points..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please provide source material in the sidebar first!")

if col3.button("💡 Explain Simply"):
    if st.session_state.user_notes.strip():
        prompt = "Explain these notes in very simple terms like I'm 10 years old:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Simplifying..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please provide source material in the sidebar first!")

if col4.button("🧪 Quiz Me"):
    if st.session_state.user_notes.strip():
        prompt = "Generate 5 multiple choice questions (with answers) based on these notes:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Generating quiz..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please provide source material in the sidebar first!")

st.divider()

# Chat section
st.subheader("💬 Chat With Your Notes")

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    is_user = msg["role"] == "user"
    
    # Hide hidden prompt prefixes applied for Quick Actions
    if is_user and any(x in msg["content"] for x in ["Summarize these notes", "Convert these notes", "Explain these notes", "Generate 5 multiple choice"]):
        continue

    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if not is_user:
            st.download_button(
                label="⬇️ Save Answer",
                data=msg["content"],
                file_name=f"ai_response_{i}.txt",
                mime="text/plain",
                key=f"download_{i}"
            )

# Chat input
if user_input := st.chat_input("Ask a specific question about your notes..."):
    if not st.session_state.user_notes.strip():
        st.warning("Please provide source material in the sidebar first!")
    else:
        system_msg = f"You are a helpful study assistant. The user has shared these notes:\n\n{st.session_state.user_notes}\n\nAnswer all questions based on these notes."

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            reply = st.write_stream(get_streaming_response([{"role": "system", "content": system_msg}] + st.session_state.messages))

        st.session_state.messages.append({"role": "assistant", "content": reply})