import streamlit as st
import json
import base64
import asyncio
import websockets
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# -----------------------------
# Load glossary
# -----------------------------
with open("glossary.json") as f:
    glossary = json.load(f)

# -----------------------------
# Streamlit setup
# -----------------------------
st.set_page_config(page_title="Live Jargon Translator", layout="wide")
st.title("🎤 Live Jargon Translator")
st.caption("Browser mic → AssemblyAI Realtime → Expanded acronyms")

API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"

def expand_jargon(text: str) -> str:
    for term, meaning in glossary.items():
        text = text.replace(term, f"{term} ({meaning})")
    return text

caption_box = st.empty()

# -----------------------------
# UI button + logic
# -----------------------------
if st.button("Start Live Translation", key="start_button"):
    st.info("🎙️ Starting… allow mic access")

    # Capture mic audio
    webrtc_ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
    )

    if webrtc_ctx.audio_receiver:
        st.success("✅ Mic connected, capturing audio…")

        audio_queue = asyncio.Queue()

        async def process_audio():
            while True:
                frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                if frames:
                    st.write(f"Captured {len(frames)} frames")  # debug
                    audio_queue.put_nowait(frames[0].to_ndarray().tobytes())

        async def debug_run():
            async with websockets.connect(
                URL,
                extra_headers={"Authorization": API_KEY},
                ping_interval=5,
                ping_timeout=20,
            ) as ws:

                async def sender():
                    while True:
                        audio_frame = await audio_queue.get()
                        if audio_frame is None:
                            break
                        await ws.send(json.dumps({
                            "audio_data": base64.b64encode(audio_frame).decode("utf-8")
                        }))

                async def receiver():
                    async for msg in ws:
                        data = json.loads(msg)
                        st.write("From AssemblyAI:", data)  # debug
                        if "text" in data and data["text"]:
                            expanded = expand_jargon(data["text"])
                            caption_box.markdown(f"**{expanded}**")

                await asyncio.gather(sender(), receiver())

        loop = asyncio.get_event_loop()
        loop.create_task(process_audio())
        loop.run_until_complete(debug_run())

