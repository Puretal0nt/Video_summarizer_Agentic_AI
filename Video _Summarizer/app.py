import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
if API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)

# Page configuration
st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="🎥",
    layout="wide"
)

st.title("Phidata YouTube AI Summarizer Agent 🎥")
st.header("Powered by Gemini 2.0 Flash Exp")

# Initialize the multimodal agent
@st.cache_resource
def initialize_agent():
    return Agent(
        name="YouTube Video Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

multimodal_agent = initialize_agent()

# Function to fetch YouTube transcript
def fetch_youtube_transcript(video_url):
    try:
        # Extract video ID from URL
        video_id = video_url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        raise RuntimeError(f"Could not retrieve transcript: {e}")

# Input for YouTube link
youtube_url = st.text_input(
    "Enter YouTube URL",
    placeholder="Paste a YouTube video link here",
    help="Provide a YouTube link for AI analysis"
)

# User query for insights
user_query = st.text_area(
    "What insights are you seeking from the video?",
    placeholder="Ask anything about the video content. The AI agent will analyze it and provide insights.",
    help="Provide specific questions or insights you want from the video."
)

# Process the YouTube link
if st.button("🔍 Analyze YouTube Video"):
    if not youtube_url:
        st.warning("Please enter a valid YouTube URL.")
    elif not user_query:
        st.warning("Please enter a query or insights you are looking for.")
    else:
        try:
            with st.spinner("Fetching transcript and analyzing..."):
                # Fetch transcript
                transcript = fetch_youtube_transcript(youtube_url)

                # Create analysis prompt
                analysis_prompt = (
                    f"""
                    The following is the transcript of a YouTube video:
                    {transcript}

                    Based on this transcript, answer the following query:
                    {user_query}

                    Provide a detailed, user-friendly, and actionable response.
                    """
                )

                # Analyze using the Gemini agent
                response = multimodal_agent.run(analysis_prompt)

            # Display the result
            st.subheader("Analysis Result")
            st.markdown(response.content)

        except RuntimeError as error:
            st.error(f"An error occurred: {error}")

