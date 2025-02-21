import streamlit as st

def get_movie_titles(graph):
    query = """
        MATCH (m:Movie)
        RETURN m.title AS title
    """

    results = graph.query(query)

    results_list = [record["title"] for record in results]
    return results_list

def get_genre_names(graph):
    query = """
        MATCH (g:Genre)
        RETURN g.genre AS genre
    """

    results = graph.query(query)

    results_list = [record["genre"] for record in results]
    return results_list

def get_actor_names(graph):
    query = """
        MATCH (a:Actor)
        RETURN a.actorName AS name
    """

    results = graph.query(query)

    results_list = [record["name"] for record in results]
    return results_list