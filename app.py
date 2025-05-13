"""
MenoMind - AI Assistant for Menopause Support
Main application file containing the Streamlit app structure
"""

import base64
import random
import gc
from datetime import datetime
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Import custom modules
from models.llm_model import llm
from models.vectorstore import vectorstore
from models.prompt_templates import answer_prompt_template
from utils.classifier import needs_retrieval
from retriever.hybrid_retrieval import hybrid_retrieve
from styles.css_styles import load_css_styles
from data.common_data import (
    common_questions,
    menopause_stages,
    wellness_tips
)
from components.sidebar import render_sidebar
from components.chat_tab import render_chat_tab
from components.resources_tab import render_resources_tab
from components.symptom_tracker_tab import render_symptom_tracker_tab
from utils.helpers import load_assets


# Page configuration
st.set_page_config(
    page_title="MenoMind",
    page_icon="🌸",
    layout="wide",
)

# Load CSS styles
st.markdown(load_css_styles(), unsafe_allow_html=True)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Chat"

# Load models and assets
@st.cache_resource(show_spinner=False)
def initialize_resources():
    return {
        "llm": llm,
        "vectorstore": vectorstore,
        "prompt_template": answer_prompt_template,
        "classifier": needs_retrieval,
        "retriever": hybrid_retrieve,
        "assets": load_assets()
    }

resources = initialize_resources()

# Reset chat function
def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_history = []
    gc.collect()

# Render sidebar with reset button
render_sidebar(wellness_tips, menopause_stages, reset_chat)

# Create tabs
tabs = st.tabs(["💬 Chat", "📚 Resources", "📊 Symptom Tracker"])

# Render each tab
with tabs[0]:
    render_chat_tab(
        common_questions=common_questions,
        resources=resources,
        classify_query=needs_retrieval,
        retrieve_context=hybrid_retrieve
    )

with tabs[1]:
    render_resources_tab(resource_images=resources["assets"]["resource_images"])

with tabs[2]:
    render_symptom_tracker_tab()