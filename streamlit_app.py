import openai
import streamlit as st

PRICE_PER_THOUSAND_TOKENS = 0.20

with st.sidebar:
    st.title('🥼🔎 OpenAI Chatbot')
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        openai.api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
        if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.total_tokens = 0

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )["choices"]:
            full_response += response["text"]
            message_placeholder.markdown(full_response + "▌")
            st.session_state.total_tokens += response.usage['total_tokens']
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

with st.sidebar:
    tokens_used = st.session_state.total_tokens
    cost = tokens_used / 1000 * PRICE_PER_THOUSAND_TOKENS
    st.subheader("Usage Information")
    st.write(f"Tokens used: {tokens_used}")
    st.write(f"Cost: ${cost:.2f}")
