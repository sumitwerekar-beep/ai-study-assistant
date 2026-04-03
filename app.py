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
st.set_page_config(page_title="AI Study Assistant", page_icon="🧠")
st.title("🧠 AI Study Assistant")

# Notes input section
st.subheader("📝 Enter or Upload Notes")

uploaded_file = st.file_uploader("Upload notes", type=["txt", "pdf", "docx"])

# Session state for notes
if "user_notes" not in st.session_state:
    st.session_state.user_notes = ""

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

    st.success("File uploaded successfully ✅")
    st.caption(f"📊 Notes: {len(st.session_state.user_notes.split())} words")
    st.markdown("### 📄 Preview")
    st.text_area("📄 File Content:", st.session_state.user_notes, height=200)

else:
    st.session_state.user_notes = st.text_area("Or paste your notes here:", height=200)

st.divider()

# Initialize chat history in session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick action buttons
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
        st.warning("Please paste your notes first!")

if col2.button("🔵 Bullet Points"):
    if st.session_state.user_notes.strip():
        prompt = "Convert these notes into clear bullet points:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Creating bullet points..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please paste your notes first!")

if col3.button("💡 Explain Simply"):
    if st.session_state.user_notes.strip():
        prompt = "Explain these notes in very simple terms like I'm 10 years old:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Simplifying..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please paste your notes first!")

if col4.button("🧪 Quiz Me"):
    if st.session_state.user_notes.strip():
        prompt = "Generate 5 multiple choice questions (with answers) based on these notes:\n" + st.session_state.user_notes
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Generating quiz..."):
            reply = get_response([{"role": "system", "content": "You are a helpful study assistant."}] + st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.warning("Please paste your notes first!")

st.divider()

# Chat section
st.subheader("💬 Chat With Your Notes")

# Display chat history
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        if not any(x in msg["content"] for x in ["Summarize these notes", "Convert these notes", "Explain these notes", "Generate 5 multiple choice"]):
            with st.chat_message("user"):
                st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])
            st.download_button(
                label="⬇️ Download",
                data=msg["content"],
                file_name="ai_notes.txt",
                mime="text/plain",
                key=f"download_{i}"
            )

# Chat input
if user_input := st.chat_input("Ask anything about your notes..."):
    if not st.session_state.user_notes.strip():
        st.warning("Please paste your notes above first!")
    else:
        system_msg = f"You are a helpful study assistant. The user has shared these notes:\n\n{st.session_state.user_notes}\n\nAnswer all questions based on these notes."

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            reply = st.write_stream(get_streaming_response([{"role": "system", "content": system_msg}] + st.session_state.messages))

        st.session_state.messages.append({"role": "assistant", "content": reply})

# Export full chat
if st.session_state.messages:
    full_chat = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
    st.download_button("📥 Export Full Chat", data=full_chat, file_name="chat_history.txt", mime="text/plain")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()