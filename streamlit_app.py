import openai
from openai import OpenAI
import streamlit as st
from tiktoken import Tokenizer
from tiktoken.tokenizer import Tokenizer

USD_TO_HKD = 7.85  # Conversion rate from USD to HKD, you can update this value based on the current exchange rate

# Function to count tokens in a text
def count_tokens(text):
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(text)
    return len(tokens)

# Function to calculate the cost in USD and HKD
def calculate_cost(token_count, tokens_per_dollar=4000, usd_to_hkd=USD_TO_HKD):
    cost_usd = token_count / tokens_per_dollar
    cost_hkd = cost_usd * usd_to_hkd
    return cost_usd, cost_hkd

with st.sidebar:
    st.title('🤖💬 OpenAI Chatbot')
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        openai.api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai.api_key = st.text_input('Enter OpenAI API token:', type='password')
        if not (openai.api_key.startswith('sk-') and len(openai.api_key) == 51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

client = OpenAI(api_key=openai.api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    tokens = count_tokens(message["content"])
    cost_usd, cost_hkd = calculate_cost(tokens)
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        st.write(f"Tokens: {tokens}, Cost: ${cost_usd:.4f} USD / ${cost_hkd:.4f} HKD")

total_tokens = sum(count_tokens(m["content"]) for m in st.session_state.messages)
total_cost_usd, total_cost_hkd = calculate_cost(total_tokens)
with st.sidebar:
    st.write(f"Total tokens used: {total_tokens}")
    st.write(f"Total cost: ${total_cost_usd:.4f} USD / ${total_cost_hkd:.4f} HKD")

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages], stream=True):
            if response.choices[0].delta.content is not None:
                full_response += response.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
