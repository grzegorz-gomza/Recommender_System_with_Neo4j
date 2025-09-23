import streamlit as st
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

# Create the LLM
llm = ChatOpenAI(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model=st.secrets["OPENAI_MODEL"],
    temperature=1,
)

# Create the Embedding model
embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])
