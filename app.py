import streamlit as st
import json
import asyncio
import websockets
import base64
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# Load glossary
with open("glossary.json") as f:
    glossary = json.load(f)

st.set_page_config(page_title="Live Jargon Translator", layout="wide")
st.title("🎤 Live Jargon Translator")
st.caption("Browser mic → AssemblyAI → Expanded acronyms")

API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

# Expand acronyms with glossary
def expand_jargon(text):
    for term, meaning in glossary.items():
        text = text.replace(term, f"{term} ({meaning})")
    return text

caption_box = st.empty()

async def transcribe():
    async with websockets.connect(
        URL,
        extra_headers={"Authorization": API_KEY},
        ping_interval=5,
        ping_timeout=20,
    ) as ws:
        async def sender():
            webrtc_ctx = webrtc_streamer(
                key="speech",
                mode=WebRtcMode.SENDONLY,
                media_stream_constraints={"audio": True, "video": False},
            )
            while webrtc_ctx.audio_receiver:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if audio_frames:
                    data = audio_frames[0].to_ndarray().tobytes()
                    await ws.send(json.dumps({
                        "audio_data": base64.b64encode(data).decode("utf-8")
                    }))
                await asyncio.sleep(0.01)

        async def receiver():
            async for msg in ws:
                data = json.loads(msg)
                if "text" in data and data["text"]:
                    expanded = expand_jargon(data["text"])
                    caption_box.markdown(f"**{expanded}**")

        await asyncio.gather(sender(), receiver())

if st.button("Start Live Translation"):
    asyncio.run(transcribe())
