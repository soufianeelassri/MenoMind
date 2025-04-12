import streamlit as st
from datetime import datetime
from models.llm import llm
from utils.classifier import needs_retrieval
from utils.hybrid_retrieval import hybrid_retrieve
from models.vectorstore import vectorstore
from models.prompt_templates import answer_prompt_template

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(
    page_title="MenoMind",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("MenoMind")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask me something about hormonal health...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        start_time = datetime.now()

        print(needs_retrieval(user_input, llm))
        if needs_retrieval(user_input, llm):
            unique_docs = hybrid_retrieve(user_input, vectorstore)
            context = "\n\n".join(doc.page_content for doc in unique_docs[:10])
        else:
            context = ""

        final_prompt = answer_prompt_template.format(context=context, question=user_input)
        final_answer = llm.invoke(final_prompt).content

        elapsed = (datetime.now() - start_time).total_seconds()
        final_answer += f"\n\n🕒 {elapsed:.2f} seconds"

        st.markdown(final_answer)
        st.session_state.chat_history.append({"role": "assistant", "content": final_answer})