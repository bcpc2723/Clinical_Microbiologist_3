import openai
import streamlit as st

PRICE_PER_THOUSAND_TOKENS = 0.20

with st.sidebar:
    st.title('🥼🔎 OpenAI Chatbot')
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        api_key = st.secrets['OPENAI_API_KEY']
    else:
        api_key = st.text_input('Enter OpenAI API token:', type='password')
        if not (api_key.startswith('sk-') and len(api_key) == 51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

client = openai.Client(api_key)

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

        response = client.chat.completions.create(
            engine="gpt-3.5-turbo",
            prompt="\n".join([f'{m["role"]}: {m["content"]}' for m in st.session_state.messages]) + "\nassistant:",
            max_tokens=150,
            n=1,
            stop=["\n"],
            temperature=0.5,
        )

        full_response = response.choices[0].text.strip()
        message_placeholder.markdown(full_response)
        st.session_state.total_tokens += response.usage['total_tokens']
    st.session_state.messages.append({"role": "assistant", "content": full_response})

with st.sidebar:
    tokens_used = st.session_state.total_tokens
    cost = tokens_used / 1000 * PRICE_PER_THOUSAND_TOKENS
    st.subheader("Usage Information")
    st.write(f"Tokens used: {tokens_used}")
    st.write(f"Cost: ${cost:.2f}")
