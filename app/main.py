import streamlit as st
import requests
from system_config import SystemConfig
import json
import os
from typing import Dict, Any
import re

st.set_page_config(page_title="Homebase",
                   page_icon="🤖",
                   layout="wide")

system_config = SystemConfig()


OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')


def filter_thinking(text: str) -> str:
    """
    Remove content between <think> tags
    """
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)


def query_ollama(model_name: str, prompt: str, system_prompt: str = None,
                 temperature: float = 0.7, top_p: float = 0.9,
                 context_size: int = 4096):
    """
    Enhanced Ollama query function with streaming support and think filter.
    """
    url = f"{OLLAMA_HOST}/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "options" : {
            "temperature": temperature,
            "seed":32,
            "num_ctx":context_size
            },
        "stream": True
    }

    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(url, json=payload, stream=True, timeout=600)

        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        # Create a placeholder for the streaming text
        message_placeholder = st.empty()
        full_response = ""
        chunk_buffer = ""
        for chunk in response.iter_lines():
            if chunk:
                # Decode the chunk and parse JSON
                chunk_data = json.loads(chunk.decode('utf-8'))
                # Extract the response text from the chunk
                chunk_text = chunk_data.get('response', '')
                chunk_buffer += chunk_text
                filtered_text = chunk_buffer
                full_response += filtered_text
                chunk_buffer = ""  # Clear buffer
                # Only update display if there's visible content
                if filtered_text.strip():
                    message_placeholder.markdown(full_response + "▌")

        # Final cleanup and display
        final_response = filter_thinking(full_response)
        message_placeholder.markdown(final_response)
        return final_response

    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


def extract_response(byte_string):
    decoded_str = byte_string.decode('utf-8')
    try:
        json_data = json.loads(decoded_str)
        return json_data.get('response', '')
    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}"


def get_available_models():
    """Get list of available models from Ollama"""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
        if response.status_code == 200:
            models = [model["name"] for model in response.json()["models"]]
            return models
        return []
    except:
        return []


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Sidebar for advanced settings
with st.sidebar:
    st.header("System Information")
    st.write(f"Device Type: N/A")

    st.header("Settings")

    # Model selection
    available_models = get_available_models()
    if available_models:
        selected_model = st.selectbox("Select Model", available_models)
    else:
        st.error("No models found. Please make sure Ollama is running.")
        selected_model = st.text_input("Enter Model Name", "llama2")

    # Advanced parameters
    st.subheader("Advanced Parameters")
    temperature = st.slider("Temperature (Creativity)", 0.0, 2.0, 0.7, 0.1,
                            help="Higher values make output more creative")

    top_p = st.slider("Top P (Nucleus Sampling)", 0.0, 1.0, 0.9, 0.05,
                      help="Controls diversity of responses")

    context_size = st.select_slider("Context Size",
                                    options=[2048, 4096, 8192, 16384, 32768],
                                    value=4096,
                                    help="Maximum context length (higher values use more memory)")

    # System prompt input
    system_prompt = st.text_area("System Prompt (Optional)",
                                 "You are a helpful AI assistant. "
                                 "Provide detailed and accurate responses quickly.")

    # Performance tips
    st.markdown("""
   ### Performance Tips:
   - Lower context size for faster responses
   - Use GPU for better performance
   - Adjust temperature based on need:
       - Lower (0.1-0.5) for factual responses
       - Higher (0.7-1.0) for creative tasks
   """)

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# Main chat interface
st.title("Chat Interface")


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input
if prompt := st.chat_input("Enter your message"):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get AI response with streaming
    with st.chat_message("assistant"):
        response = query_ollama(
            selected_model,
            prompt,
            system_prompt,
            temperature,
            top_p,
            context_size
        )

    # Add AI response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
