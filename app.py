import streamlit as st
import json

# Load glossary
with open("glossary.json") as f:
    glossary = json.load(f)

st.set_page_config(page_title="Live Jargon Translator", layout="wide")
st.title("🎤 Live Jargon Translator")
st.caption("Speak into your mic. Construction/tech acronyms will be expanded automatically.")

# Expand acronyms with glossary
def expand_jargon(text):
    for term, meaning in glossary.items():
        text = text.replace(term, f"{term} ({meaning})")
    return text

# Placeholder for captions
caption_box = st.empty()

# Demo mode (fake input for now)
sample_lines = [
    "Please update the GCGR before we finalize the SOV.",
    "Check the UoM in the estimate.",
    "BIM files must be included in this package."
]

if st.button("Run Demo"):
    for line in sample_lines:
        expanded = expand_jargon(line)
        caption_box.markdown(f"**{expanded}**")
