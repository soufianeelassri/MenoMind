"""
MenoMind - Sidebar Component
Renders the application sidebar
"""

import random
import streamlit as st

def render_sidebar(wellness_tips, menopause_stages, reset_callback):
    """
    Renders the sidebar with information and reset button
    
    Args:
        wellness_tips (list): List of wellness tips
        menopause_stages (dict): Dictionary of menopause stages and descriptions
        reset_callback (function): Callback function to reset the chat
    """
    with st.sidebar:
        
        # About section
        st.markdown("""
        <h4 style='font-family: "Dancing Script", cursive;'>About MenoMind</h4>
        """, unsafe_allow_html=True)
        st.markdown("""
            <p style='font-size: 0.9rem;'>Your trusted AI companion for navigating menopause with confidence and ease. 
            Get reliable information, personalized advice, and compassionate support.</p>
        """, unsafe_allow_html=True)
        
        # Menopause Stages in the sidebar
        st.markdown("""
        <h4 style='font-family: "Dancing Script", cursive;'>Menopause Stages</h4>
        """, unsafe_allow_html=True)
        for stage, description in menopause_stages.items():
            st.markdown(f"""
                <div class="info-card">
                    <h4 style='color: #FF69B4; margin-top: 0;'>{stage}</h4>
                    <p style='font-size: 0.9rem;'>{description}</p>
                </div>
            """, unsafe_allow_html=True)

         # Reset button
        if st.button("Reset conversation"):
            reset_callback()