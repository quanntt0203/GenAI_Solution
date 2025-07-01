# pip install -qU langchain-ollama
# pip install langchain
# pip install streamlit

import streamlit as st
from ollama import Client, ChatResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv(".env")

# Set the default values for OLLAMA_HOST and OLLAMA_MODEL
ollama_host = os.environ.get("OLLAMA_HOST")
ollama_model = os.environ.get("OLLAMA_MODEL")

if "chat_model" not in st.session_state:
    st.session_state.chat_model = ollama_model

if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []

model = ChatOllama(model=st.session_state.chat_model, base_url=ollama_host)
# user message in 'user' key
# ai message in 'assistant' key
def get_history():
    chat_history = []
    for chat in st.session_state['chat_history']:
        prompt = HumanMessagePromptTemplate.from_template(chat['user'])
        chat_history.append(prompt)
        ai_message = AIMessagePromptTemplate.from_template(chat['assistant'])
        chat_history.append(ai_message)

    return chat_history

def generate_response(chat_histroy):
    chat_template = ChatPromptTemplate.from_messages(chat_histroy)
    chain = chat_template|model|StrOutputParser()
    response = chain.invoke({})

    return response

#client config
#client = Client(host=ollama_host)
st.set_page_config(layout='wide')
st.title(":brain: Alpha - AI Assistant - βeta")
st.header(f"Chat with LLM model :baby:")

st.info(":computer: model host: {host}".format(host=ollama_host))
with st.form("llm-form", clear_on_submit=False):
    st.markdown(":sparkles: Select model and enter your question below:", unsafe_allow_html=True)
    chat_model = st.selectbox("Select model", ["llama3.1", "deepseek-r1"], index=0, label_visibility="collapsed", placeholder="Select model", help="Select the model you want to use for chat.")
    text = st.text_area("User Input", placeholder="Type your question here...", key="widget", label_visibility="collapsed")
    submit = st.form_submit_button("Ask")

if submit and text:
    with st.spinner("Generating response..."):
        if not chat_model:
            chat_model = ollama_model

        st.session_state.chat_model = chat_model
        # response: ChatResponse = client.chat(model=st.session_state.chat_model, messages=[
        #     {
        #         'role': 'user',
        #         'content': text,
        #     }],
        #     stream=False
        # )
        #st.write("**:brain: Bot response: ", response.message.content, unsafe_allow_html=True)

        prompt = HumanMessagePromptTemplate.from_template(text)
        chat_history = get_history()
        chat_history.append(prompt)
        response = generate_response(chat_history)

        st.session_state['chat_history'].append({'user': text, 'assistant': response})

st.write("## Chat History :page_facing_up:")
for chat in reversed(st.session_state['chat_history']):
       st.write(f"**:adult: User**: {chat['user']}", unsafe_allow_html=True)
       st.write(f"**:brain: Assistant**: {chat['assistant']}", unsafe_allow_html=True)
       st.write("---")

# To run the Streamlit app, execute the following command in the terminal:
# streamlit run D:\AI\ai-fine-tune\chat\chat_8888.py --server.port 8888
#export OLLAMA_HOST=http://10.21.10.36:7869
#export OLLAMA_MODEL=deepseek-r1
