"""
MenoMind - Symptom Tracker Component
Renders the symptom tracker with recommendation generation
"""

import streamlit as st
from datetime import datetime
import base64
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from models.llm_model import llm

import os
import platform
import re
import sys

try:
    # Windows-specific fix for WeasyPrint
    if platform.system() == "Windows":
        gtk_path = r"C:\Program Files\GTK3\bin"
        if os.path.exists(gtk_path):
            os.add_dll_directory(gtk_path)
    from weasyprint import HTML
except Exception as e:
    st.error(f"WeasyPrint error: {e}")


def render_symptom_tracker_tab():
    """
    Renders the symptom tracker tab with form and LLM-generated recommendations
    """

    with st.form("symptom_tracker_form"):
        st.markdown(
            "<h4 style='font-family: \"Dancing Script\", cursive;'>Rate your symptoms (0 = None, 10 = Severe)</h4>",
            unsafe_allow_html=True
        )

        symptoms = {
            "Hot flashes": "Sudden feelings of warmth spreading throughout your body",
            "Night sweats": "Excessive sweating during sleep that may soak your nightclothes or bedding",
            "Sleep difficulties": "Problems falling asleep or staying asleep",
            "Mood changes": "Irritability, anxiety, or mood swings",
            "Fatigue": "Feeling tired or lacking energy",
            "Vaginal dryness": "Discomfort during intercourse or general dryness",
            "Joint pain": "Aches or stiffness in your joints",
            "Brain fog": "Difficulty concentrating or remembering things"
        }

        symptom_values = {}
        symptom_names = list(symptoms.keys())

        for i in range(0, len(symptom_names), 2):
            col1, col2 = st.columns(2)
            with col1:
                name1 = symptom_names[i]
                symptom_values[name1] = st.slider(name1, 0, 10, 0, help=symptoms[name1])
            if i + 1 < len(symptom_names):
                with col2:
                    name2 = symptom_names[i + 1]
                    symptom_values[name2] = st.slider(name2, 0, 10, 0, help=symptoms[name2])

        additional_info = st.text_area("Additional notes or symptoms not listed above:")
        current_treatments = st.text_area("Current treatments or lifestyle changes you're trying:")

        submitted = st.form_submit_button("Get Personalized Recommendations")

    if submitted:
        active_symptoms = [(s, v) for s, v in symptom_values.items() if v > 0]

        if not active_symptoms and not additional_info:
            st.warning("Please rate at least one symptom or provide additional information.")
            return

        symptom_text = "\n".join([f"- {s}: {v}/10" for s, v in active_symptoms])
        prompt = f"""
Please provide personalized recommendations for a woman experiencing the following menopause symptoms:

Symptoms:
{symptom_text}

Additional information: {additional_info or "None provided"}
Current treatments/lifestyle changes: {current_treatments or "None provided"}

Please provide:
1. A brief interpretation of these symptoms
2. 3-5 specific, evidence-based recommendations
3. Lifestyle adjustments
4. When to consult a healthcare provider

Use a compassionate, supportive tone.
        """

        try:
            with st.spinner("Generating personalized recommendations..."):
                response = llm.invoke(prompt)

            st.markdown(
                """
                <div style="background-color: #f8f9fa; border-radius: 10px; padding: 10px; margin-top: 20px; margin-bottom: 20px; border-left: 5px solid #FF69B4;">
                    <h3 style='font-family: "Dancing Script", cursive; text-align: center;'>Your Personalized Recommendations</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(response.content, unsafe_allow_html=True)

            st.markdown(
                """
                <div style="background-color: #edf7ed; border-radius: 10px; padding: 10px; margin-top: 20px; margin-bottom: 20px;">
                    <p style="font-style: italic; text-align: center;">
                        ⚠️ These recommendations are for informational purposes only and do not constitute medical advice.
                        Always consult a healthcare provider before making changes to your regimen.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # ------------------------ PDF GENERATION ------------------------ #
            def create_report_pdf() -> bytes:
                df = pd.DataFrame(active_symptoms, columns=["Symptom", "Rating"])
                fig, ax = plt.subplots(figsize=(9, 3.5))
                bars = ax.barh(df["Symptom"], df["Rating"], color="#FF69B4")
                ax.set_xlim(0, 10)
                ax.set_title("Symptom Severity (0–10 scale)")
                ax.set_xlabel("Severity")
                ax.bar_label(bars)
                plt.tight_layout(pad=1.2)
                plt.subplots_adjust(left=0.25, right=0.9)  # margins for better fit

                img_buf = BytesIO()
                plt.savefig(img_buf, format="png", bbox_inches='tight', dpi=150)
                plt.close()
                img_buf.seek(0)
                chart_img = base64.b64encode(img_buf.read()).decode("utf-8")

                # Format the LLM response content for HTML
                formatted_content = response.content
                
                # First, handle section headers (numbered headings)
                formatted_content = re.sub(r'(\d+)\.\s+(.*?):', r'<h3>\1. \2</h3>', formatted_content)
                
                # Replace markdown-style formatting with HTML
                formatted_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted_content)
                formatted_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted_content)
                
                # Handle special formatting for labeled content like "Vaginal lubricants:"
                formatted_content = re.sub(r'([A-Za-z\s]+):', r'<strong>\1:</strong>', formatted_content)
                
                # Better handling for asterisk bullet points
                formatted_content = re.sub(r'^\s*\*\s+(.*?)$', r'<p>• \1</p>', formatted_content, flags=re.MULTILINE)
                
                # Convert standard bullet points
                formatted_content = re.sub(r'^\s*-\s+(.*?)$', r'<p>• \1</p>', formatted_content, flags=re.MULTILINE)
                
                # Handle paragraphs - wrap text blocks in <p> tags
                paragraphs = formatted_content.split('\n\n')
                formatted_paragraphs = []
                for p in paragraphs:
                    # Skip if it's already a heading or bullet point
                    if not (p.startswith('<h') or p.startswith('<p>•')):
                        if p.strip() and not p.strip().startswith('<'):
                            p = f'<p>{p}</p>'
                    formatted_paragraphs.append(p)
                formatted_content = '\n'.join(formatted_paragraphs)
                
                # Clean up any remaining newlines not in paragraphs
                formatted_content = formatted_content.replace('\n', ' ')
                formatted_content = re.sub(r'<p>\s+', '<p>', formatted_content)
                formatted_content = re.sub(r'\s+</p>', '</p>', formatted_content)
                
                # Add some space between elements for better readability
                formatted_content = formatted_content.replace('</p><p>', '</p>\n<p>')
                formatted_content = formatted_content.replace('</h3><p>', '</h3>\n<p>')

                html_report = f"""
                <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                            .header {{ text-align: center; }}
                            .section {{ margin-top: 20px; }}
                            .chart {{ text-align: center; margin: 0; }}
                            .footer {{ margin-top: 30px; font-style: italic; text-align: center; }}
                            h3 {{ margin-top: 20px; margin-bottom: 10px; color: #333; }}
                            h4 {{ margin-top: 15px; margin-bottom: 5px; color: #444; }}
                            p {{ margin-bottom: 10px; }}
                            .recommendations p {{ margin-left: 15px; }}
                            strong {{ font-weight: bold; }}
                            em {{ font-style: italic; }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <h1>MenoMind: Personal Symptom Report</h1>
                            <p>Generated on {datetime.now().strftime("%Y-%m-%d")}</p>
                        </div>
                        <div class="section">
                            <h2>Symptom Assessment</h2>
                            <div class="chart" style="text-align: center;">
                                <img src="data:image/png;base64,{chart_img}" width="350" style="max-width: 90%; height: auto;">
                            </div>
                        </div>
                        <div class="section">
                            <h2>Additional Information</h2>
                            <p><strong>Notes:</strong> {additional_info or "None provided"}</p>
                            <p><strong>Current treatments:</strong> {current_treatments or "None provided"}</p>
                        </div>
                        <div class="section">
                            <h2>Personalized Recommendations</h2>
                            <div class="recommendations">
                                {formatted_content}
                            </div>
                        </div>
                        <div class="footer">
                            <p>These recommendations are for informational purposes only and do not constitute medical advice.
                            Always consult a healthcare provider before making changes.</p>
                            <p>© MenoMind {datetime.now().year}</p>
                        </div>
                    </body>
                </html>
                """

                return HTML(string=html_report).write_pdf()

            # ------------------------ DOWNLOAD BUTTON ------------------------ #
            try:
                pdf_bytes = create_report_pdf()
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"MenoMind_Report_{datetime.now().strftime('%Y-%m-%d')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
                st.info("Please check your environment or contact support.")

        except Exception as e:
            st.error(f"Error generating recommendations: {e}")
            st.info("Please try again later or contact support.")