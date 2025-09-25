import streamlit as st
import assemblyai as aai
import json

# Load glossary
with open("glossary.json") as f:
    glossary = json.load(f)

st.set_page_config(page_title="Live Jargon Translator", layout="wide")
st.title("🎤 Live Jargon Translator")
st.caption("Browser mic → AssemblyAI → Expanded acronyms")

aai.settings.api_key = st.secrets["ASSEMBLYAI_API_KEY"]

def expand_jargon(text):
    for term, meaning in glossary.items():
        text = text.replace(term, f"{term} ({meaning})")
    return text

caption_box = st.empty()

# Track state so we don’t re-run setup on each rerun
if "started" not in st.session_state:
    st.session_state["started"] = False

def start_transcription():
    transcriber = aai.RealtimeTranscriber(
        sample_rate=16000,
        encoding="pcm16"
    )

    @transcriber.on("transcript")
    def on_transcript(transcript: aai.RealtimeTranscript):
        if transcript.text:
            expanded = expand_jargon(transcript.text)
            caption_box.markdown(f"**{expanded}**")

    with transcriber:
        st.info("⚡ Listening… (but not yet connected to browser mic)")
        transcriber.connect()

# Button with unique key
if st.button("Start Live Translation", key="start_button"):
    if not st.session_state["started"]:
        st.session_state["started"] = True
        start_transcription()

