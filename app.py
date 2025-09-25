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

if st.button("Start Live Translation"):
    transcriber = aai.RealtimeTranscriber(
        sample_rate=16000,
        encoding="pcm16"
    )

    # Attach handlers
    @transcriber.on("transcript")
    def on_transcript(transcript: aai.RealtimeTranscript):
        if transcript.text:
            expanded = expand_jargon(transcript.text)
            caption_box.markdown(f"**{expanded}**")

    # This will block until stopped
    with transcriber:
        st.info("⚡ Listening… but not yet wired to browser mic")
        transcriber.connect()

if st.button("Start Live Translation"):
    asyncio.run(transcribe())
