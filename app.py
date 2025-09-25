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

def handle_transcript(transcript: aai.RealtimeTranscript):
    if transcript.text:
        expanded = expand_jargon(transcript.text)
        caption_box.markdown(f"**{expanded}**")

if st.button("Start Live Translation"):
    # Instead of asyncio.run, let SDK handle it
    transcriber = aai.RealtimeTranscriber(
        on_transcript=handle_transcript,
        sample_rate=16000,
    )
    with transcriber:
        st.info("⚡ Listening… start speaking!")
        transcriber.stream()  # blocking call handled by SDK


if st.button("Start Live Translation"):
    asyncio.run(transcribe())
