import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Create the LLM
llm = ChatOpenAI(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model=st.secrets["OPENAI_MODEL"],
    temperature=1,  # must be 1 for some models
    max_tokens=2000,
    stop=None,            # explicitly clear stop
).bind(stop=None)         # also clear in runtime bindings


# Create the Embedding model
embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPENAI_API_KEY"])
