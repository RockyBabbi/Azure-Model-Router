import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AZURE_OPENAI_ENDPOINT=your-endpoint-here
AZURE_OPENAI_DEPLOYMENT=model-router
AZURE_OPENAI_KEY=your-subscription-key
AZURE_OPENAI_API_VERSION=2025-01-01-preview


# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

# Streamlit page setup
st.set_page_config(page_title="Azure OpenAI Chatbot", layout="wide")
st.title("Azure OpenAI - Model Router Demo")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_used" not in st.session_state:
    st.session_state.model_used = "model-router"

# Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box
if prompt := st.chat_input("Type your message…"):
    # Display user message in chat
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare messages for API call
    messages_for_api = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]

    # Container for streaming response
    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""
        model_router_model = None

        # Streaming from Azure OpenAI
        for chunk in client.chat.completions.create(
            model=deployment,
            stream=True,
            messages=messages_for_api,
            max_tokens=8192,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        ):
            if not getattr(chunk, "choices", []) or getattr(chunk.choices[0].delta, "content", None) is None:
                continue
            model_router_model = chunk.model
            token = chunk.choices[0].delta.content or ""
            full_response += token
            response_container.markdown(full_response)

        # Update model info and save assistant response
        if model_router_model:
            st.session_state.model_used = model_router_model
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Display current model
        st.title(f"**Model used:** {st.session_state.model_used}")

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.model_used = "model-router"
    st.rerun()
