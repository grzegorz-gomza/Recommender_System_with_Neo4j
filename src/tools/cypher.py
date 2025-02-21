import streamlit as st
from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

from chat.llm import llm
from database.graph import graph
from prompts.cypher_prompts import CYPHER_GENERATION_TEMPLATE

# Create the Cypher prompt
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

# Create the Cypher QA chain
recommend_movies_relationships = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    cypher_prompt=cypher_prompt,
    verbose=True,
    allow_dangerous_requests=True,
)
