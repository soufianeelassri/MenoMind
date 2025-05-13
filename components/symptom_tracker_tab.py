"""
MenoMind - Symptom Tracker Tab Component
Renders the symptom tracker form
"""

from datetime import datetime
import streamlit as st

def render_symptom_tracker_tab():
    """
    Renders the symptom tracker tab with form for logging symptoms
    """
    # Symptom tracking form
    with st.form("symptom_tracker"):
        st.write("""<h4 style='font-family: "Dancing Script", cursive;'>
                 Log Today's Symptoms</h4>
                 """, unsafe_allow_html=True)
        st.date_input("Date", datetime.now().date())
        st.write("""<h4 style='font-family: "Dancing Script", cursive;'>
                 Symptom Intensity (0-10)</h4>
                 """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Hot Flashes", 0, 10, 0)
            st.slider("Night Sweats", 0, 10, 0)
            st.slider("Mood Changes", 0, 10, 0)
        with col2:
            st.slider("Sleep Disturbances", 0, 10, 0)
            st.slider("Fatigue", 0, 10, 0)
            st.slider("Joint Pain", 0, 10, 0)
        
        st.text_area("Additional Notes", placeholder="Any other symptoms or observations...")
        
        st.form_submit_button("Save Symptom Data")