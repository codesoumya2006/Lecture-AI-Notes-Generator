import whisper
import streamlit as st

@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")
