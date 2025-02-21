import streamlit as st
import PyPDF2
import docx2txt
import requests
import re
from googlesearch import search
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import textstat

# Custom CSS for Purple & Black Theme
st.markdown(
    """
    <style>
    body {
        background-color: #0d0d0d;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #1e1e2e;
        color: white;
    }
    .big-title {
        font-size:28px !important;
        font-weight: bold;
        text-align: center;
        color: #a855f7;
    }
    .big-subtitle {
        font-size:22px !important;
        font-weight: bold;
        text-align: center;
        color: #bbbbbb;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
        color: white;
    }
    .ats-score {
        font-size:26px !important;
        font-weight: bold;
        color: #ff9f43;
        text-align: center;
        border-radius: 8px;
        background: #2c2c54;
        padding: 15px;
    }
    .job-title {
        font-size:18px !important;
        font-weight: bold;
        color: #a855f7;
    }
    .sidebar-footer {
        font-size:14px !important;
        text-align: center;
        color: #bbbbbb;
    }
    .job-box {
        background-color: #262626;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar for Project Info
st.sidebar.markdown("## About This Project")
st.sidebar.write(
    "🚀 This tool helps job seekers **optimize their resumes** for Applicant Tracking Systems (ATS) "
    "and **find the best job opportunities** across **200+ platforms** like LinkedIn, Indeed, and Glassdoor."
)
st.sidebar.markdown("---")
st.sidebar.markdown("### ✨ Created by")
st.sidebar.markdown("**Aditya Pande & Gauri Dhamale**")
st.sidebar.markdown("---")

# Main Title
st.markdown('<p class="big-title">📄 ATS Resume Scanner & Job Finder</p>', unsafe_allow_html=True)
st.markdown('<p class="big-subtitle">Optimize Your Resume & Find Jobs from 200+ Sites</p>', unsafe_allow_html=True)

# User Inputs
st.markdown('<p class="big-font">🎯 What job are you looking for?</p>', unsafe_allow_html=True)
job_title = st.text_input("", placeholder="e.g., Senior Software Engineer")

st.markdown('<p class="big-font">🔍 Enter job keywords (comma-separated)</p>', unsafe_allow_html=True)
custom_keywords = st.text_area("", placeholder="e.g., Python, Machine Learning, AWS, API")

st.markdown('<p class="big-font">📂 Upload Resume (PDF/DOCX)</p>', unsafe_allow_html=True)
uploaded_resume = st.file_uploader("", type=["pdf", "docx"])

# Functions for Resume Processing
def extract_text(file):
    """Extract text from resume (PDF or DOCX)"""
    text = ""
    if file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif file.name.endswith(".docx"):
        text = docx2txt.process(file)
    return text

def extract_all_words(text):
    """Extract all words from the resume (excluding stopwords)"""
    words = re.findall(r'\b\w+\b', text.lower())  
    filtered_words = [word for word in words if word not in ENGLISH_STOP_WORDS and len(word) > 2]
    return list(set(filtered_words))  

def calculate_ats_score(text, user_keywords):
    """Calculate ATS score based on keyword matching, readability, and formatting"""
    score = 0
    max_score = 100

    # ✅ 1. Keyword Match Score
    industry_keywords = [
        "software", "developer", "engineer", "python", "java", "cloud", "api", "sql", "docker",
        "machine learning", "aws", "kubernetes", "cybersecurity", "blockchain", "flutter", "django",
        "data science", "tensorflow", "react", "vue", "angular", "fintech", "big data", "robotics"
    ]
    combined_keywords = list(set(industry_keywords + user_keywords))

    found_keywords = [word for word in combined_keywords if word.lower() in text.lower()]
    keyword_score = (len(found_keywords) / len(combined_keywords)) * 40  

    # ✅ 2. Readability Score
    readability = textstat.flesch_reading_ease(text)
    readability_score = max(0, min(30, (readability / 100) * 30))  

    # ✅ 3. Formatting Score
    has_contact = "email" in text.lower() or "phone" in text.lower() or "linkedin" in text.lower()
    has_skills = "skills" in text.lower()
    has_experience = "experience" in text.lower() or "work experience" in text.lower()

    formatting_score = sum([has_contact, has_skills, has_experience]) * 10  

    # ✅ Final ATS Score Calculation
    score = keyword_score + readability_score + formatting_score

    return round(score, 2), found_keywords

def google_job_search(query):
    """Search for jobs on Google across 200+ platforms"""
    job_sites = [
        "linkedin.com", "indeed.com", "glassdoor.com", "monster.com", "ziprecruiter.com",
        "weworkremotely.com", "stackoverflow.com/jobs", "angel.co/jobs", "careerbuilder.com",
        "remotive.io", "simplyhired.com", "hired.com", "fiverr.com", "upwork.com", "toptal.com",
        "hackernews.com", "remoteok.io", "jobspresso.co", "arc.dev"
    ]
    search_query = f"{query} site:" + " OR site:".join(job_sites)

    job_results = []
    try:
        for i, result in enumerate(search(search_query, num_results=10)):
            try:
                job_title = result.split("/")[2] if "/" in result else "Job Listing"
                job_summary = f"This job is available on **{job_title}**. Click the link to explore further."
                job_results.append({"index": i+1, "title": job_title, "href": result, "summary": job_summary})
            except IndexError:
                continue  
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")

    return job_results

# Process Resume
if uploaded_resume:
    resume_text = extract_text(uploaded_resume)
    
    st.markdown('<p class="big-font">📜 Extracted Resume Text</p>', unsafe_allow_html=True)
    st.text_area("", resume_text, height=200)

    # ✅ Calculate ATS Score
    ats_score, matched_keywords = calculate_ats_score(resume_text, custom_keywords.split(","))
    
    st.markdown(f'<p class="ats-score">🎯 ATS Resume Score: {ats_score}/100</p>', unsafe_allow_html=True)

    # ✅ Search for Jobs
    if st.button("🔍 Find Matching Jobs"):
        job_results = google_job_search(f"{job_title} {custom_keywords}")
        st.markdown("## 🔍 Found Jobs Across 200+ Sites and Important Links to Explore")
        for job in job_results:
            st.markdown(f'<div class="job-box">{job["index"]}. {job["summary"]}</div>', unsafe_allow_html=True)
            st.markdown(f"🔹 [Explore Job]({job['href']})")

