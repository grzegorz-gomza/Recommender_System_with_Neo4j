from typing import List, Any
from langchain_core.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import MessagesPlaceholder
from langchain.prompts.chat import ChatPromptTemplate

from chat.llm import llm
import streamlit as st
from database.graph import graph
from utils import get_session_id

from tools.vector_recommender import recommend_similar_movies
from tools.cypher import recommend_movies_relationships
from tools.user_preferences import recommend_movies_user_preferences
from prompts.llm_prompts import AGENT_PROMPT


class MovieRecommenderTools:
    """Class to manage and create movie recommendation tools."""

    @staticmethod
    def create_general_chat_tool() -> Tool:
        """Create the general chat tool."""

        chat_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a movie expert providing information about movies.",
                ),
                MessagesPlaceholder(
                    "user_watched_movies"
                ),  # This placeholder will hold extra information about watched movies
                ("human", "{input}"),
            ]
        )

        chat_chain = chat_prompt | llm | StrOutputParser()

        return Tool.from_function(
            name="General Chat",
            description="For general movie chat not covered by other tools",
            func=chat_chain.invoke,
        )

    @staticmethod
    def create_description_based_tool() -> Tool:
        """Create the movie recommendation based on description tool."""
        return Tool.from_function(
            name="Movie recommendation based on description",
            description="For when you need to find similar movies based on their description",
            func=recommend_similar_movies,
        )

    @staticmethod
    def create_relationship_based_tool() -> Tool:
        """Create the movie recommendation based on relationships tool."""
        return Tool.from_function(
            name="Movie recommendation based on relationships",
            description="For when you need to find similar movies based on their relationships",
            func=recommend_movies_relationships,
        )

    @staticmethod
    def create_preference_based_tool() -> Tool:
        """Create the movie recommendation based on user preferences tool."""
        return Tool.from_function(
            name="Movie recommendation based on user preferences",
            description="For when you need to find similar movies based on user preferences",
            func=recommend_movies_user_preferences,
        )

    @classmethod
    def create_tools(cls) -> List[Tool]:
        """Create and return all available tools."""
        return [
            cls.create_general_chat_tool(),
            cls.create_description_based_tool(),
            cls.create_relationship_based_tool(),
            cls.create_preference_based_tool(),
        ]


class MovieRecommenderAgent:
    """Class to manage the movie recommendation agent."""

    def __init__(self, available_tools: List[Tool]):
        """Initialize the movie recommendation agent with tools."""
        self.tools = available_tools
        self.agent_prompt = self._create_agent_prompt()
        self.agent = self._create_agent()
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True
        )
        self.chat_agent = self._create_chat_agent()

    def _create_agent_prompt(self) -> PromptTemplate:
        """Create the agent prompt template."""
        return PromptTemplate.from_template(AGENT_PROMPT)

    def _create_agent(self) -> Any:
        """Create the LangChain agent."""
        return create_react_agent(llm, self.tools, self.agent_prompt)

    def _create_chat_agent(self) -> RunnableWithMessageHistory:
        """Create the chat agent with message history."""
        return RunnableWithMessageHistory(
            self.executor,
            lambda: self._get_chat_history(),
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def _get_chat_history(self) -> Neo4jChatMessageHistory:
        """Get the chat message history from Neo4j."""
        return Neo4jChatMessageHistory(session_id=get_session_id(), graph=graph)

    def response(self, user_input: str, user_watched_movies: List[str]) -> str:
        """Generate a response based on user input and watched movies."""
        payload = {"input": user_input, "user_watched_movies": user_watched_movies}
        response = self.chat_agent.invoke(
            payload, {"configurable": {"session_id": get_session_id()}}
        )
        return response["output"]


class MovieRecommenderApp:
    """Class to manage the movie recommendation application."""

    tools = MovieRecommenderTools.create_tools()
    agent = MovieRecommenderAgent(available_tools=tools)

    @staticmethod
    def generate_response(
        user_input: str,
        user_watched_movies: List[str],
        agent: MovieRecommenderAgent = agent,
    ) -> str:
        """
        Generate a response based on user input and the list of movies the user has watched.

        Args:
            user_input (str): The input provided by the user for which a response is to be generated.
            user_watched_movies (List[str]): A list of movie titles that the user has already watched.

        Returns:
            str: The generated response as a string.

        Raises:
            ValueError: If the input arguments are of incorrect type.
        """
        try:
            # Input validation
            if not isinstance(user_input, str):
                raise ValueError("user_input must be a string")
            if not isinstance(user_watched_movies, list) or not all(
                isinstance(movie, str) for movie in user_watched_movies
            ):
                raise ValueError("user_watched_movies must be a list of strings")

            return agent.response(user_input, user_watched_movies)

        except Exception as e:
            # Log the error
            print(f"An error occurred: {str(e)}")
            # You can also log this to a file or another logging mechanism
            raise
