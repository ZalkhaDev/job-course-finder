import streamlit as st
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer, util
import torch

# =======================
# Streamlit setup
# =======================
st.set_page_config(page_title="Intelligent Job & Course Finder", page_icon="💼", layout="wide")
st.title("💼 Intelligent AI Job & Course Finder")
st.write("Enter your skills and get personalized job & course recommendations!")

# =======================
# User input
# =======================
user_input = st.text_input("Enter your skills (comma separated):", "Python, SQL, Machine Learning")

if not user_input.strip():
    st.warning("Please enter at least one skill.")
    st.stop()

user_skills = [skill.strip() for skill in user_input.split(",")]
user_skills_str = " ".join(user_skills)

# =======================
# Load embedding model
# =======================
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()
user_embedding = model.encode(user_skills_str, convert_to_tensor=True)

# =======================
# Fetch live jobs from JSearch API
# =======================
@st.cache_data(ttl=3600)
def fetch_jobs(skills):
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {"query": ",".join(skills), "num_pages": 1}
    response = requests.get(url, headers=headers, params=params)
    data = response.json().get("data", [])
    jobs_list = []
    for job in data:
        jobs_list.append({
            "Job": job.get("job_title", ""),
            "Company": job.get("employer_name", ""),
            "Description": job.get("job_description", "")
        })
    return pd.DataFrame(jobs_list)

jobs_df = fetch_jobs(user_skills)

# =======================
# Local courses dataset (larger and diverse)
# =======================
courses_df = pd.DataFrame({
    "Course": [
        "Intro to Python Programming",
        "Machine Learning with TensorFlow",
        "Web Development Bootcamp",
        "Cybersecurity Fundamentals",
        "Excel for Business",
        "Digital Marketing Essentials",
        "UI/UX Design Fundamentals",
        "Project Management Professional (PMP)"
    ],
    "Description": [
        "Python Basics, SQL, Programming",
        "Machine Learning, TensorFlow, AI, Python",
        "HTML, CSS, JavaScript, React",
        "Networking, Security, Linux, Ethical Hacking",
        "Excel, Data Analysis, Business Reporting",
        "Marketing, SEO, Social Media, Analytics",
        "UI Design, UX Research, Figma, Prototyping",
        "Project Management, Planning, Leadership"
    ]
})

# =======================
# Function to rank by semantic similarity
# =======================
def rank_by_similarity(df, text_column, user_emb):
    if df.empty:
        return df
    embeddings = model.encode(df[text_column].tolist(), convert_to_tensor=True)
    cos_scores = util.cos_sim(user_emb, embeddings)[0]
    df["Match %"] = (cos_scores * 100).round(1)
    return df.sort_values(by="Match %", ascending=False)

jobs_df = rank_by_similarity(jobs_df, "Description", user_embedding)
courses_df = rank_by_similarity(courses_df, "Description", user_embedding)

# =======================
# Display results
# =======================
st.subheader("📌 Recommended Jobs")
if not jobs_df.empty:
    st.dataframe(jobs_df[["Job", "Company", "Match %"]].reset_index(drop=True), use_container_width=True)
else:
    st.write("No jobs found for these skills.")

st.subheader("📚 Recommended Courses")
if not courses_df.empty:
    st.dataframe(courses_df[["Course", "Match %"]].reset_index(drop=True), use_container_width=True)
else:
    st.write("No courses found for these skills.")
