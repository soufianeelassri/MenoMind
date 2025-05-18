"""
MenoMind - Chat Tab Component
Renders the chat interface and handles user interactions
"""

import gc
from datetime import datetime
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from utils.helpers import format_chat_history_for_prompt

def render_chat_tab(common_questions, resources, classify_query, retrieve_context):
    """
    Renders the chat tab with message history and input
    
    Args:
        common_questions (list): List of common questions as quick suggestions
        resources (dict): Dictionary of resources including LLM, vectorstore, etc.
        classify_query (function): Function to classify if a query needs retrieval
        retrieve_context (function): Function to retrieve context for a query
    """
    llm = resources["llm"]
    vectorstore = resources["vectorstore"]
    answer_prompt_template = resources["prompt_template"]
    user_avatar = "👩‍🦰"
    assistant_avatar = "🌸"
    
    # Quick question suggestions
    st.markdown("""
    <h4 style='font-family: "Dancing Script", cursive;'>Quick Questions</h4>
    """, unsafe_allow_html=True)

    # Handle quick question selection via session state
    if "selected_question" not in st.session_state:
        st.session_state.selected_question = None

    quick_questions_html = "".join([
        f"""<div class="quick-question" onclick="
            parent.postMessage({{command: 'streamlit:setComponentValue', key: 'selected_question', value: '{q.replace("'", "\\'")}'}}, '*');
        ">{q}</div>"""
        for q in common_questions
    ])
    st.markdown(f'<div class="quick-questions-container">{quick_questions_html}</div>', unsafe_allow_html=True)

    # Create a column layout to constrain chat content
    chat_col1, _ = st.columns([1, 3])
        
    # Display all messages from history
    for msg_data in st.session_state.messages:
        role = msg_data["role"]
        avatar = user_avatar if role == "user" else assistant_avatar
            
        with st.chat_message(role, avatar=avatar):
            st.markdown(f"<div style='font-size: 14px;'>{msg_data['content']}</div>", unsafe_allow_html=True)
            
            # Add response time for assistant messages INSIDE the message container
            if role == "assistant" and "elapsed" in msg_data:
                st.markdown(f"""
                    <div style='font-size:10px; margin-top:4px;'>
                        ⏱️ Response time: {msg_data["elapsed"]:.2f} seconds
                    </div>
                """, unsafe_allow_html=True)
    
    @st.cache_data(show_spinner=False)
    def _classify_query(_query, _llm_instance):
        return classify_query(_query, _llm_instance)

    @st.cache_data(show_spinner=False)
    def _retrieve_context(_query, _vectorstore_instance):
        docs = retrieve_context(_query, _vectorstore_instance)
        return "\n\n".join(doc.page_content for doc in docs[:10])
    
    # Input box for user questions
    user_input = st.chat_input("Ask questions about menopause, symptoms, treatments, lifestyle changes, or emotional support.")

    if user_input:
        # Switch to chat tab if user sends a message
        st.session_state.current_tab = "Chat"
        
        # Add user message to chat history
        st.session_state.chat_history.append(HumanMessage(content=user_input))

        # Process query
        start_time = datetime.now()
        conversation_history_str = format_chat_history_for_prompt(st.session_state.chat_history)

        if _classify_query(user_input, llm):
            context = _retrieve_context(user_input, vectorstore)
        else:
            context = ""

        final_prompt = answer_prompt_template.format(
            context=context,
            question=user_input,
            conversation_history=conversation_history_str
        )

        # Display user message
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(f"<div style='font-size: 14px;'>{user_input}</div>", unsafe_allow_html=True)
            
        # Add to messages
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Stream the assistant response
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
                        response_placeholder.markdown(f"<div style='font-size: 14px;'>{streamed_response_content}▌</div>", unsafe_allow_html=True)
                
                elapsed_time = (datetime.now() - start_time).total_seconds()
                
                # Final update with consistent styling
                response_placeholder.markdown(
                    f"<div style='font-size: 14px;'>{streamed_response_content}</div>"
                    f"<div style='font-size:10px; margin-top:4px;'>"
                    f"⏱️ Response time: {elapsed_time:.2f} seconds</div>",
                    unsafe_allow_html=True
                )
                
                # Add to chat history and messages
                st.session_state.chat_history.append(AIMessage(content=streamed_response_content))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": streamed_response_content,
                    "elapsed": elapsed_time
                })
                
            except Exception as e:
                st.error(f"Error streaming response: {e}")
                streamed_response_content = "I apologize, but I encountered an issue generating my response."
                response_placeholder.markdown(f"<div style='font-size: 14px;'>{streamed_response_content}</div>", unsafe_allow_html=True)
                
                # Add error message to history
                st.session_state.chat_history.append(AIMessage(content=streamed_response_content))
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": streamed_response_content,
                    "elapsed": (datetime.now() - start_time).total_seconds()
                })

        gc.collect()
        
    with chat_col1:    
        # Chat Footer with disclaimer
        st.markdown("""
            <div class="fixed-bottom-warning"">
                ⚠️ MenoMind is an educational tool and not a substitute for professional medical advice.
                Always consult with a healthcare provider for medical concerns.
            </div>
        """, unsafe_allow_html=True)