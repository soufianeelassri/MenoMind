"""
MenoMind - Helper Functions
Contains utility functions used across the application
"""

import base64
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

@st.cache_data(show_spinner=False)
def load_logo_base64():
    """
    Loads the logo image as base64 encoded string
    """
    try:
        with open("./assets/menopause.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

@st.cache_data(show_spinner=False)
def load_resource_images():
    """
    Loads the resource images as base64 encoded strings
    """
    resources = {}
    resource_files = {
        "hot_flash": "./assets/hot_flash.jpeg",
        "nutrition": "./assets/nutrition.jpeg",
        "sleep": "./assets/sleep.jpeg",
        "wellness": "./assets/wellness.jpeg",
    }
    
    for key, path in resource_files.items():
        try:
            with open(path, "rb") as f:
                resources[key] = base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            resources[key] = None
    
    return resources

@st.cache_data(show_spinner=False)
def load_assets():
    """
    Loads all assets used in the application
    """
    return {
        "logo": load_logo_base64(),
        "resource_images": load_resource_images()
    }

def format_chat_history_for_prompt(chat_hist_list_of_messages):
    """
    Formats the chat history for the prompt template
    """
    formatted_history_lines = []
    history_to_format = chat_hist_list_of_messages[:-1]
    
    for msg in history_to_format:
        if isinstance(msg, HumanMessage):
            formatted_history_lines.append(f"User Question: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted_history_lines.append(f"MenoMind Response: {msg.content}")
            
    return "\n".join(formatted_history_lines)