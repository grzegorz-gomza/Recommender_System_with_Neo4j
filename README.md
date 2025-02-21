# Recommender Chat for Netflix

This project provides an interactive movie recommendation experience powered by a conversational AI agent. It leverages the capabilities of Neo4j (a graph database), Langchain (a framework for building LLM applications), and Streamlit (for creating the user interface).

## Features

The core of this application is a Langchain agent equipped with four specialized tools:

1.  **Movie Chatbot:** A conversational chatbot restricted (via system prompt) to discussing movies only.  It provides a natural language interface for general movie-related inquiries.

2.  **Relationship-Based Recommendations:** This tool leverages the power of Neo4j's graph database.  It uses an LLM to generate Cypher queries based on user input. These queries explore relationships between movies, actors, genres, and other entities within the database to provide recommendations.  For example, it might recommend movies starring the same actors as a movie the user enjoyed.

3.  **Preference-Based Recommendations:** This tool takes user preferences into account, including:
    *   Liked movies
    *   Preferred genres
    *   Favorite actors
    *   Movies already watched (to avoid redundant recommendations)

    Based on this information, the system queries the Neo4j database to identify and suggest similar movies that align with the user's profile.

4.  **Description Similarity Recommendations:** This tool utilizes embeddings (vector representations) of movie descriptions. It calculates the cosine similarity between the embeddings of different movies. This allows the system to recommend movies with plots and themes similar to those the user has enjoyed.

## Architecture

The system is designed to intelligently select the appropriate tool based on the user's input.  A system prompt guides the Langchain agent in choosing the correct tool for each interaction. This ensures that the user receives the most relevant and helpful responses.

*   **Neo4j GraphDB:** Stores movie data, relationships (e.g., "actor starred in movie", "movie belongs to genre"), and user preferences.
*   **Langchain:** Provides the framework for building the conversational agent, managing the tools, and interacting with the LLM and Neo4j.
*   **Streamlit:** Creates a user-friendly web interface for interacting with the recommendation agent.

## Running the application

The application is deployed on the Streamlit platform.

Since this is a training project and not a production-ready product, it is possible that:

*  The provided API key may be deactivated, as the costs are higher than the author can accept.
*  The Neo4j Aura instance may be paused, as it is a free-tier database.

If either of these issues occurs, please contact the author to resolve them.

## Cloning and running the application localy
Provide some brief and clear instructions how to run the project on your own. For example:

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Neo4j:**
    *   In order to run the app you need to create your own Neo4j Database instance.
    *   Install and configure Neo4j.  [Go to neo4j aura documentation](https://neo4j.com/docs/aura/classic/auradb/getting-started/create-database/)

4.  **Configure environment variables:** 
    *   Provide the following information about your instance in .streamlit/secrets.toml file:

    ```bash
    NEO4J_URI=""
    NEO4J_USERNAME=""
    NEO4J_PASSWORD=""
    AURA_INSTANCEID=""
    AURA_INSTANCENAME=""

    OPENAI_API_KEY=""
    OPENAI_MODEL="gpt-4o-mini"
    ```

5.  **Create Neo4j Database:**
    *   Import movie data into Neo4j using the Jupyter Notebook file src/database/create_netflix_db.ipynb


6.  **Run the Streamlit app:**

    ```bash
    streamlit run src/main.py
    ```


## Contributing
Feel free to submit issues or pull requests to improve functionality or documentation.

## License
This project is licensed under the MIT License.

