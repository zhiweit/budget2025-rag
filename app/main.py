import streamlit as st
import uuid
import atexit
from llama_index.core.chat_engine.types import StreamingAgentChatResponse
from tracing import launch_phoenix, close_phoenix
from chat_engine import similarity_postprocessor
from vectors import vsi
from llama_index.core.chat_engine.types import ChatMode
from chat_engine import chat_engine_llm, response_synthesizer, SIMILARITY_TOP_K, sentence_transformer_reranker, chat_engine_llm
from db import chat_store
from llama_index.core.memory import ChatMemoryBuffer
import random
import time
from llama_index.core.agent.react.base import ReActAgent


if 'chat_engine' not in st.session_state:
    # Put your startup code here
    chat_engine = vsi.as_chat_engine(
        chat_mode=ChatMode.BEST,
        llm=chat_engine_llm,
        similarity_top_k=SIMILARITY_TOP_K,
        node_postprocessors=[similarity_postprocessor, sentence_transformer_reranker],
        response_synthesizer=response_synthesizer,
        streaming=True,
    )

    st.session_state['chat_engine'] = chat_engine
    thread_id = str(uuid.uuid4())
    st.session_state['thread_id'] = thread_id
    print(f"Thread ID: {thread_id}")
    # Launch Phoenix tracing
    launch_phoenix()
    print("Phoenix launched at port 6006")
    print("Startup code ran")


# Register cleanup function to be called at shutdown
def cleanup():
    # Add your cleanup code here
    close_phoenix()
    print("Phoenix closed")


# Register the cleanup handler
atexit.register(cleanup)


# Streamed response emulator
def response_generator(question: str):
    if 'chat_engine' not in st.session_state:
        response = random.choice(
            [
                "Sorry, model is not initialized yet.",
                "Please wait a moment, model is initializing.",
                "Initializing model...",
            ]
        )
        for word in response.split():
            yield word + " "
            time.sleep(0.05)

    else:    
        chat_engine: ReActAgent = st.session_state['chat_engine']
        thread_id = st.session_state['thread_id']
        chat_history = chat_store.get_messages(thread_id)

        memory = ChatMemoryBuffer.from_defaults(
            chat_store=chat_store,
            chat_store_key=thread_id,
            chat_history=chat_history,
            llm=chat_engine_llm,
        )

        chat_engine.memory = memory

        streaming_response: (
            StreamingAgentChatResponse
        ) = chat_engine.stream_chat(question)
        for token in streaming_response.response_gen:
            yield token


st.title("Simple chat")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if "role" in message and "content" in message:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me questions about the budget."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt))
    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )