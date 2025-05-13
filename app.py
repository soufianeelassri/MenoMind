import base64
import gc
from datetime import datetime
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from models.llm_model import llm
from models.vectorstore import vectorstore
from models.prompt_templates import answer_prompt_template
from utils.classifier import needs_retrieval
from retriever.hybrid_retrieval import hybrid_retrieve

@st.cache_data(show_spinner=False)
def load_logo_base64():
    with open("./assets/menopause.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_resource(show_spinner=False)
def get_llm():
    return llm

@st.cache_resource(show_spinner=False)
def get_vectorstore():
    return vectorstore

@st.cache_resource(show_spinner=False)
def get_prompt_template():
    return answer_prompt_template

@st.cache_resource(show_spinner=False)
def get_classifier():
    return needs_retrieval

@st.cache_resource(show_spinner=False)
def get_retriever():
    return hybrid_retrieve

llm = get_llm()
vectorstore = get_vectorstore()
answer_prompt_template = get_prompt_template()
needs_retrieval = get_classifier()
hybrid_retrieve = get_retriever()
menomind_logo_base64 = load_logo_base64()

st.set_page_config(
    page_title="MenoMind",
    page_icon="🌸",
    layout="centered",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def reset_chat():
    st.session_state.messages = []
    st.session_state.chat_history = []
    gc.collect()
    
st.markdown("""
    <style>
    
           /* Remove blank space at top and bottom */ 
           .block-container {
               padding-top: 3rem;
               padding-bottom: 0rem;
            }
    
    </style>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 15px;'>
            <img src="data:image/png;base64,{menomind_logo_base64}" width="60">
            <h1 style='color: #FF69B4; font-family: "Dancing Script", cursive; font-size: 44px;'>MenoMind</h1>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div>
            <p style='color: #999; font-family: "Dancing Script", cursive; font-size: 19px;'>
                Your trusted companion for menopause wellness and care 🌸
            </p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.button("Clear ↺", on_click=reset_chat)

st.markdown("""
    <style>
    .fixed-bottom-warning {
        position: fixed;
        bottom: 10px;
        color: #999;
        font-size: 10px;
        font-weight: 600;
        font-family: "Dancing Script", cursive;
        padding: 0 0 20px 0;
        margin-left: 180px;
        z-index: 9999;
    }
    </style>
    <div class="fixed-bottom-warning">
        MenoMind may sometimes be incorrect. Please verify critical information.
    </div>
""", unsafe_allow_html=True)

user_avatar = "👩‍🦰"
assistant_avatar = "🤖"

@st.cache_data(show_spinner=False)
def classify_query(_query, _llm_instance):
    return needs_retrieval(_query, _llm_instance)

@st.cache_data(show_spinner=False)
def retrieve_context(_query, _vectorstore_instance):
    docs = hybrid_retrieve(_query, _vectorstore_instance)
    return "\n\n".join(doc.page_content for doc in docs[:10])

def format_chat_history_for_prompt(chat_hist_list_of_messages):
    formatted_history_lines = []
    history_to_format = chat_hist_list_of_messages[:-1]
    for msg in history_to_format:
        if isinstance(msg, HumanMessage):
            formatted_history_lines.append(f"User Question: {msg.content}")
        elif isinstance(msg, AIMessage):
            formatted_history_lines.append(f"MenoMind Response: {msg.content}")
    return "\n".join(formatted_history_lines)

for msg_data in st.session_state.messages:
    role = msg_data["role"]
    avatar = user_avatar if role == "user" else assistant_avatar
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg_data["content"])

user_input = st.chat_input("What would you like to know about menopause?")

if user_input:
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(user_input)
    
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    start_time = datetime.now()
    conversation_history_str = format_chat_history_for_prompt(st.session_state.chat_history)

    if classify_query(user_input, llm):
        context = retrieve_context(user_input, vectorstore)
    else:
        context = ""

    final_prompt = answer_prompt_template.format(
        context=context,
        question=user_input,
        conversation_history=conversation_history_str
    )

    with st.chat_message("assistant", avatar=assistant_avatar):
        response_placeholder = st.empty()
        streamed_response_content = ""
        try:
            for chunk in llm.stream(final_prompt):
                chunk_text = ""
                if hasattr(chunk, 'content') and chunk.content is not None:
                    chunk_text = chunk.content
                elif isinstance(chunk, str):
                    chunk_text = chunk

                if chunk_text:
                    streamed_response_content += chunk_text
                    response_placeholder.markdown(streamed_response_content + "|")
            
            elapsed_time = (datetime.now() - start_time).total_seconds()
            response_placeholder.markdown(
                f"{streamed_response_content}\n\n"
                f"<div style='font-size:10px; color:#999; margin-top:4px;'>"
                f"⏱️ Response time: {elapsed_time:.2f} seconds</div>",
                unsafe_allow_html=True
            )
        except Exception as e:
            st.error(f"Error streaming response: {e}")
            streamed_response_content = "I apologize, but I encountered an issue generating my response."
            response_placeholder.markdown(streamed_response_content)

    st.session_state.messages.append({"role": "user", "content": user_input})
    
    final_answer_for_history = streamed_response_content
    elapsed_for_history = (datetime.now() - start_time).total_seconds()
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_answer_for_history,
        "elapsed": elapsed_for_history
    })
    
    st.session_state.chat_history.append(AIMessage(content=final_answer_for_history))

    gc.collect()