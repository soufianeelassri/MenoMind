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
        
        # Daily wellness tip
        st.markdown("""
        <h4 style='font-family: "Dancing Script", cursive;'>Wellness Tip of the Day</h4>
        """, unsafe_allow_html=True)
        daily_tip = random.choice(wellness_tips)
        st.markdown(f"""
            <div class="info-card" style='background-color: #f0fff4; border: 1px solid #72e897; border-left-color: #72e897; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);'>
                <h4 style='color: #28a745; margin-top: 0;'>💡 Daily Tip</h4>
                <p style='font-size: 0.9rem;'>{daily_tip}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Resources
        st.markdown("""
        <h4 style='font-family: "Dancing Script", cursive;'>Additional Resources</h4>
        """, unsafe_allow_html=True)
        st.markdown("[North American Menopause Society](https://www.menopause.org/)")
        st.markdown("[Women's Health Initiative](https://www.whi.org/)")
        st.markdown("[The Menopause Charity](https://www.themenopausecharity.org/)")

        # Reset button
        if st.button("Reset conversation"):
            reset_callback()