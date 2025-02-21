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
    page_title="YouTube AI Summarizer",
    page_icon="🎥",
    layout="wide"
)

# Custom Styling
st.markdown(
    """
    <style>
    body {
        background: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...') no-repeat center center fixed;
        background-size: cover;
        color: #FFFFFF;
        font-family: 'Arial', sans-serif;
    }
    .header {
        background: rgba(0, 0, 0, 0.8);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-bottom: 20px;
    }
    .header h1 {
        color: #FFD700;
        font-size: 50px;
        margin: 0;
        text-transform: uppercase;
    }
    .header p {
        color: #CCCCCC;
        font-size: 18px;
        margin-top: 5px;
    }
    .input-container {
        background: rgba(255, 255, 255, 0.2);
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .input-field {
        font-size: 18px;
        font-family: 'Arial', sans-serif;
        color: #000;
    }
    .textarea-field {
        font-size: 20px;
        font-family: 'Arial', sans-serif;
        color: #000;
    }
    .button-style {
        background: #6A0DAD;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 20px;
        border-radius: 5px;
        cursor: pointer;
        font-family: 'Arial', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Header Section
st.markdown(
    """
    <div class='header'>
        <h1>Tutor.AI</h1>
        <p>Your ultimate gateway to AI-powered insights and learning</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Section
st.sidebar.title("About Tutor.AI")
st.sidebar.markdown(
    """
    **Product Summary**
    - Tutor.AI is an innovative platform designed to extract insights from YouTube videos using advanced AI technologies.

    **Product Made By**
    - Developed by Aditya Pande and Gauri Sopan Dhamale.
    """
)

# Initialize AI Agent
@st.cache_resource
def initialize_agent():
    return Agent(
        name="YouTube Video Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )
multimodal_agent = initialize_agent()

# UI Inputs with improved layout
with st.container():
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    youtube_url = st.text_input(
        "Enter YouTube URL", 
        placeholder="Paste a YouTube video link here", 
        help="Provide a valid YouTube link for analysis",
        key='youtube_url',
        label_visibility="visible"
    )
    user_query = st.text_area(
        "What insights are you seeking?", 
        placeholder="Ask about the video content...", 
        help="Provide specific questions or topics you'd like insights on.",
        key='user_query',
        label_visibility="visible"
    )
    st.markdown("</div>", unsafe_allow_html=True)

# Fetch YouTube transcript function
def fetch_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript])
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
        raise RuntimeError(f"Could not retrieve transcript: {e}")

# Analyze Video Button with Feedback
if st.button("🔍 Analyze Video", help="Click to analyze video content"):
    if not youtube_url:
        st.warning("Please enter a valid YouTube URL.")
    elif not user_query:
        st.warning("Please enter a question or insight request.")
    else:
        try:
            with st.spinner("Fetching transcript and analyzing... 🚀"):
                transcript = fetch_youtube_transcript(youtube_url)
                analysis_prompt = f"""
                The following is the transcript of a YouTube video:
                {transcript}
                
                Based on this transcript, answer the following query:
                {user_query}
                
                Provide a detailed, user-friendly, and actionable response.
                """
                response = multimodal_agent.run(analysis_prompt)
            
            # Display Output
            st.success("Analysis Complete! ✅")
            st.subheader("Analysis Result")
            st.markdown(response.content)
        except RuntimeError as error:
            st.error(f"An error occurred: {error}")

# Add Support Button (Buy Me a Coffee)
st.markdown("---")
st.markdown("**Enjoying this app? Support my work:**")
st.markdown(
    """
    <form action="https://buymeacoffee.com/aditya_pande" method="get" target="_blank">
        <button class='button-style'>☕ Buy Me a Coffee</button>
    </form>
    """,
    unsafe_allow_html=True
)

