"""
MenoMind - Chat Tab Component
Renders the chat interface and handles user interactions
"""

import gc
from datetime import datetime
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from utils.helpers import format_chat_history_for_prompt
from config import DEFAULT_RERANKING_ENABLED, DEFAULT_REPACKING_ENABLED, DEFAULT_REPACKING_METHOD

def render_chat_tab(resources, classify_query, retrieve_context):
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
    
    # Add retrieval settings to session state if not present
    if "use_reranking" not in st.session_state:
        st.session_state.use_reranking = DEFAULT_RERANKING_ENABLED
    if "use_repacking" not in st.session_state:
        st.session_state.use_repacking = DEFAULT_REPACKING_ENABLED
    if "repacking_method" not in st.session_state:
        st.session_state.repacking_method = DEFAULT_REPACKING_METHOD

    # Create a main content area
    main_container = st.container()
    
    # Add retrieval settings in a row
    settings_cols = st.columns(4)
    
    with settings_cols[0]:
        st.markdown("""<h4 style='font-family: "Dancing Script", cursive;'>
                    Retrieval Settings
                    </h4>""", unsafe_allow_html=True)
    
    with settings_cols[1]:
        st.toggle("Use Reranking", key="use_reranking", 
                help="Reranking improves retrieval quality by reordering results using a cross-encoder model")
    
    with settings_cols[2]:
        st.toggle("Use Document Repacking", key="use_repacking",
                help="Repacking groups similar documents together for better context")
                
    with settings_cols[3]:
        if st.session_state.use_repacking:
            st.selectbox("Repacking Method", ["similarity", "token_limit"], key="repacking_method",
                        help="Similarity: Group by semantic similarity, Token Limit: Group by token count")
        
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
        try:
            return classify_query(_query, _llm_instance)
        except Exception as e:
            print(f"Error in query classification: {e}")
            # Default to True if classification fails
            return True

    @st.cache_data(show_spinner=False, ttl=600)
    def _retrieve_context(_query, _vectorstore_instance, use_reranking, use_repacking, repacking_method):
        try:
            docs = retrieve_context(
                _query, 
                _vectorstore_instance, 
                use_reranking=use_reranking,
                use_repacking=use_repacking,
                repacking_method=repacking_method
            )
            if docs:
                return "\n\n".join(doc.page_content for doc in docs[:10])
            else:
                return ""
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return ""
    
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

        try:
            needs_retrieval = _classify_query(user_input, llm)
        except Exception as e:
            needs_retrieval = False
            print(f"Error checking if query needs retrieval: {e}")

        context = ""
        if needs_retrieval:
            context = _retrieve_context(
                user_input, 
                vectorstore,
                st.session_state.use_reranking,
                st.session_state.use_repacking,
                st.session_state.repacking_method
            )

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
        
    # Chat Footer with disclaimer
    st.markdown("""
        <div class="fixed-bottom-warning"">
            ⚠️ MenoMind is an educational tool and not a substitute for professional medical advice.
            Always consult with a healthcare provider for medical concerns.
        </div>
    """, unsafe_allow_html=True)