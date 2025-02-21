import io
import streamlit as st
from utils import clean_uploaded_data, initialize_session_state
from database.graph import graph
from chat.agent import MovieRecommenderApp
import prompts.cypher_queries as cypher_queries

# Type hinting imports
from typing import List, Optional

# Get sensitive information
openai_api_key = st.secrets["OPENAI_API_KEY"]
openai_model = st.secrets["OPENAI_MODEL"]


def main() -> None:
    """
    Entry point for the Streamlit application. Sets up the page, user interface,
    handles preference uploads, and user-agent interactions.
    """

    # Set Streamlit page configuration
    st.set_page_config(
        page_title="Netflix Movie Recommender 🎥",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply custom styling
    with open("src/style.css", "r") as style_file:
        css = style_file.read()
    st.markdown(css, unsafe_allow_html=True)

    st.title("🎥 Netflix Movie Recommender")

    # Initialize session state
    initialize_session_state()

    # Sidebar for user preferences
    display_sidebar(graph)

    # Main chat interface
    display_chat_interface()


def display_sidebar(graph) -> None:
    """
    Creates and manages the sidebar components where users can upload
    or manually input their preferences.
    """
    st.sidebar.header("🎬 Your Preferences")
    st.sidebar.markdown(
        "Set your preferences below to get personalized recommendations – just like Netflix!"
    )

    with st.sidebar.expander("🔧 Set User Preferences"):
        movie_titles = cypher_queries.get_movie_titles(graph)
        genre_names = cypher_queries.get_genre_names(graph)
        actor_names = cypher_queries.get_actor_names(graph)

        # Handle file upload for preferences
        txt_file = st.file_uploader("📥 Upload your preferences (TXT)", type="txt")
        if st.button("📤 Upload Preferences"):
            upload_preferences(txt_file)

        # Handle manual entry of preferences
        st.write("Or enter your preferences manually 👇")
        handle_manual_preferences(movie_titles, genre_names, actor_names)

        if st.button("💾 Save Preferences"):
            save_preferences()


def upload_preferences(txt_file: Optional[io.BytesIO]) -> None:
    """
    Handles uploading and parsing a TXT file with user preferences.

    Args:
        txt_file (Optional[io.BytesIO]): The file uploaded by the user.
    """

    if txt_file is not None:
        with st.spinner("Uploading TXT File..."):
            try:
                lists = [clean_uploaded_data(line) for line in txt_file]
                st.session_state.user_movies = lists[0]
                st.session_state.user_actors = lists[1]
                st.session_state.user_genres = lists[2]
                st.session_state.user_watched = lists[3]
                st.success("📂 Preferences Uploaded Successfully!", icon="✅")
            except Exception as e:
                st.error("Upload Failed", icon="❌")
                st.error(e)
    else:
        st.warning("Please upload a valid TXT file.", icon="⚠️")


def handle_manual_preferences(
    movie_titles: List[str], genre_names: List[str], actor_names: List[str]
) -> None:
    """
    Handles manual entry of user preferences.

    Args:
        movie_titles (List[str]): List of available movie titles.
        genre_names (List[str]): List of available genres.
        actor_names (List[str]): List of available actors.
    """
    st.session_state.user_movies = st.multiselect(
        "🎥 Select Your Favorite Movies",
        movie_titles,
        st.session_state.get("user_movies", []),
        max_selections=10,
    )
    st.write("You selected:", st.session_state.user_movies)

    st.session_state.user_actors = st.multiselect(
        "⭐ Choose Favorite Actors",
        actor_names,
        st.session_state.get("user_actors", []),
        max_selections=10,
    )
    st.write("You selected:", st.session_state.user_actors)

    st.session_state.user_genres = st.multiselect(
        "🎭 Pick Favorite Genres",
        genre_names,
        st.session_state.get("user_genres", []),
        max_selections=10,
    )

    st.session_state.user_watched = st.multiselect(
        "👀 Mark Movies You've Watched",
        movie_titles,
        st.session_state.get("user_watched", []),
    )


def save_preferences() -> None:
    """
    Saves the current user preferences into a downloadable TXT file.
    """
    with st.spinner("Preparing Download..."):
        try:
            file_content = f"""\
{st.session_state.user_movies}
{st.session_state.user_actors}
{st.session_state.user_genres}
{st.session_state.user_watched}"""

            buffer = io.BytesIO(file_content.encode())
            buffer.seek(0)

            st.download_button(
                label="📥 Download Preferences",
                data=buffer,
                file_name="session_preferences.txt",
                mime="text/plain",
            )
            st.success("Preferences Ready to Download!", icon="✅")
        except Exception as e:
            st.error("Download Failed", icon="❌")
            st.error(e)


def display_chat_interface() -> None:
    """
    Displays the main chat interface for interacting with the recommendation agent.
    """
    st.markdown("## 💻 Chat with the Recommender")

    # Display chat history
    for i, message in enumerate(st.session_state.get("chat_history", [])):
        role = "user" if i % 2 == 0 else "assistant"
        with st.chat_message(role):
            st.markdown(message[-1])

    # Input for user queries
    user_message = st.chat_input("🔎 Ask for Recommendations:")
    if user_message:
        handle_user_query(user_message)


def handle_user_query(user_message: str) -> None:
    """
    Processes user queries and generates responses using the recommendation agent.

    Args:
        user_message (str): The message or query entered by the user.
    """
    st.session_state.chat_history = st.session_state.get("chat_history", [])
    st.session_state.chat_history.append(("User", user_message))

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.spinner("Generating Recommendations..."):
        try:
            response = MovieRecommenderApp.generate_response(
                user_input=user_message,
                user_watched_movies=st.session_state.get("user_watched", []),
            )
            st.session_state.chat_history.append(("Assistant", response))

            with st.chat_message("assistant"):
                st.markdown(response)
        except Exception as e:
            st.error("Error generating response.")
            st.error(e)


if __name__ == "__main__":
    main()
