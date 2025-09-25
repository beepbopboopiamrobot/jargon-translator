import streamlit as st
import openai
import json
import tempfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# Load glossary
with open("glossary.json") as f:
    glossary = json.load(f)

st.set_page_config(page_title="Live Jargon Translator", layout="wide")
st.title("🎤 Live Jargon Translator")
st.caption("Speak into your mic. Acronyms will be expanded automatically.")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Expand acronyms with glossary
def expand_jargon(text):
    for term, meaning in glossary.items():
        text = text.replace(term, f"{term} ({meaning})")
    return text

# Placeholder for live captions
caption_box = st.empty()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.text = ""

    def recv_audio(self, frame):
        # Save audio chunk to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            tmpfile.write(frame.to_ndarray().tobytes())
            tmpfile.flush()
            try:
                # Send audio to Whisper API
                with open(tmpfile.name, "rb") as audio_file:
                    transcript = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                text = transcript.text
                expanded = expand_jargon(text)
                caption_box.markdown(f"**{expanded}**")
            except Exception as e:
                caption_box.write(f"Error: {e}")
        return frame

webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False}
)
