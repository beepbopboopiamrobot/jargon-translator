import streamlit as st
import json
import websocket
import threading
import base64
import pyaudio

# Load glossary
with open("glossary.json") as f:
    glossary = json.load(f)

st.set_page_config(page_title="Live Jargon Translator", layout="wide")
st.title("🎤 Live Jargon Translator")
st.caption("Live speech → expanded acronyms (via AssemblyAI)")

API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

# Expand acronyms
def expand_jargon(text):
    for term, meaning in glossary.items():
        text = text.replace(term, f"{term} ({meaning})")
    return text

# Placeholder for captions
caption_box = st.empty()

def run():
    ws = websocket.WebSocketApp(
        URL,
        header={"Authorization": API_KEY},
        on_message=on_message,
        on_error=lambda ws, e: st.error(f"Error: {e}"),
        on_close=lambda ws, c, m: st.warning("Connection closed"),
        on_open=on_open,
    )
    ws.run_forever()

def on_message(ws, message):
    data = json.loads(message)
    if "text" in data and data["text"]:
        expanded = expand_jargon(data["text"])
        caption_box.markdown(f"**{expanded}**")

def on_open(ws):
    def send_audio():
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=3200)
        while True:
            data = stream.read(3200)
            ws.send(json.dumps({"audio_data": base64.b64encode(data).decode("utf-8")}))
    threading.Thread(target=send_audio, daemon=True).start()

if st.button("Start Live Translation"):
    threading.Thread(target=run, daemon=True).start()
