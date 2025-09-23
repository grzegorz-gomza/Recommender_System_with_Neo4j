from typing import Any
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import tool
from src.chat.llm import llm
import streamlit as st
from src.database.graph import graph
from langchain_neo4j import Neo4jGraph
from src.prompts.cypher_prompts import (
    CYPHER_MOVIE_SIMILARITY_SEARCH_TEMPLATE,
    CYPHER_GENRE_SIMILARITY_SEARCH_TEMPLATE,
    CYPHER_ACTOR_SIMILARITY_SEARCH_TEMPLATE,
)
from src.prompts.llm_prompts import USER_PREFERENCES_RECOMMENDATION_PROMPT


class MovieRecommenderUserPreferences:
    def __init__(
        self,
        graph_instance: Neo4jGraph,
    ):
        """Initialize the MovieRecommender with the necessary dependencies.

        Args:
            session_state (st.session_state): Streamlit session state containing user preferences
            graph_instance (Neo4jGraph): Neo4j graph instance
        """
        self.session_state = st.session_state
        self.graph = graph_instance
        self._setup_llm_chain()

    def _setup_llm_chain(self) -> None:
        """Initialize the LLM chain with the prompt template and output parser."""
        self.prompt_template = PromptTemplate.from_template(
            USER_PREFERENCES_RECOMMENDATION_PROMPT
        )
        self.chat_chain = self.prompt_template | llm | StrOutputParser()

    def _query_graph(self, template: str, params: dict) -> list:
        """Execute a Cypher query on the graph with the given template and parameters.

        Args:
            template (str): Cypher query template
            params (dict): Parameters to substitute into the template

        Returns:
            list: List of records from the query result
        """
        try:
            result = self.graph.query(template, params)
            return result
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def get_similar_movies(self) -> list[str]:
        """Retrieve movies similar to the ones the user has watched.

        Returns:
            list[str]: List of similar movie titles
        """
        user_movies = self.session_state.user_movies
        user_watched_movies = self.session_state.user_watched

        similar_movies = []
        for movie in user_movies:
            params = {
                "movie_title": movie,
                "user_movies": user_movies,
                "user_watched_movies": user_watched_movies,
            }
            result = self._query_graph(CYPHER_MOVIE_SIMILARITY_SEARCH_TEMPLATE, params)
            similar_movies.extend([record["RecommendedMovie"] for record in result])
        return similar_movies

    def get_genre_recommendations(self) -> list[str]:
        """Retrieve movie recommendations based on the user's favorite genres.

        Returns:
            list[str]: List of movie titles from the selected genres
        """
        user_genres = self.session_state.user_genres
        user_watched_movies = self.session_state.user_watched

        params = {
            "user_genres": user_genres,
            "user_watched_movies": user_watched_movies,
        }
        result = self._query_graph(CYPHER_GENRE_SIMILARITY_SEARCH_TEMPLATE, params)
        return [record["rec.title"] for record in result]

    def get_actor_recommendations(self) -> list[str]:
        """Retrieve movie recommendations based on the user's favorite actors.

        Returns:
            list[str]: List of movie titles featuring the selected actors
        """
        user_actors = self.session_state.user_actors
        user_watched_movies = self.session_state.user_watched

        params = {
            "user_actors": user_actors,
            "user_watched_movies": user_watched_movies,
        }
        result = self._query_graph(CYPHER_ACTOR_SIMILARITY_SEARCH_TEMPLATE, params)
        return [record["rec.title"] for record in result]

    def get_recommendations(self) -> dict:
        """Combine all recommendations into a single structured response.

        Returns:
            dict: Dictionary containing similar movies, genre-based, and actor-based recommendations
        """
        similar_movies = self.get_similar_movies()
        genre_movies = self.get_genre_recommendations()
        actor_movies = self.get_actor_recommendations()

        return {
            "similar_movies": similar_movies,
            "genre_movies": genre_movies,
            "actor_movies": actor_movies,
        }

    def generate_recommendation_response(self) -> str:
        """Use the LLM chain to generate a human-readable recommendation response.

        Returns:
            str: Formatted recommendation response from the LLM
        """
        recommendations = self.get_recommendations()
        try:
            response = self.chat_chain.invoke(
                {
                    "similar_movies": recommendations["similar_movies"],
                    "user_actors": recommendations["actor_movies"],
                    "user_genres": recommendations["genre_movies"],
                }
            )
            return response
        except Exception as e:
            print(f"Error generating recommendation response: {e}")
            return "Sorry, I couldn't generate recommendations at this time."


@tool("recommend_movies_user_preferences", return_direct=True)
def recommend_movies_user_preferences(input, actual_graph: Neo4jGraph = graph) -> str:
    """
    Recommends movies based on user preferences using a Neo4j graph.

    Args:
        input: The input data for movie recommendations.
        actual_graph (Neo4jGraph, optional): The Neo4j graph instance for querying.
            Defaults to a pre-configured graph instance.

    Returns:
        str: A formatted string containing movie recommendations.
    """

    recommender = MovieRecommenderUserPreferences(graph_instance=actual_graph)
    return recommender.generate_recommendation_response()
