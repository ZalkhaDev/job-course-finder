import streamlit as st
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =======================
# Streamlit setup
# =======================
st.set_page_config(page_title="AI Job & Course Finder", page_icon="💼", layout="wide")
st.title("💼 AI Job & Course Finder")
st.write("Enter your skills and get personalized job & course recommendations!")

# Display your API key (for testing, remove later)
# st.write("Your API key is:", st.secrets["RAPIDAPI_KEY"])

user_input = st.text_input("Enter your skills (comma separated):", "Python, SQL")

# =======================
# Helper functions
# =======================

def fetch_jobs(user_skills):
    """Fetch jobs from JSearch API and return a DataFrame"""
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": ",".join(user_skills),
        "num_pages": 1
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json().get("data", [])
    
    jobs_list = []
    for job in data:
        jobs_list.append({
            "Job": job.get("job_title", ""),
            "Description": job.get("job_description", ""),
            "Company": job.get("employer_name", "")
        })
    return pd.DataFrame(jobs_list)


def fetch_courses(user_skills):
    """Fetch courses from Udemy API (example)"""
    url = "https://www.udemy.com/api-2.0/courses/"
    # Udemy API requires OAuth token; this is a placeholder
    headers = {
        "Authorization": f"Bearer {st.secrets.get('UDEMY_KEY', '')}"
    }
    params = {"search": " ".join(user_skills), "page": 1, "page_size": 20}
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json().get("results", [])
    
    courses_list = []
    for course in data:
        courses_list.append({
            "Course": course.get("title", ""),
            "Description": course.get("headline", ""),
            "URL": course.get("url", "")
        })
    return pd.DataFrame(courses_list)


def rank_similarity(df, user_skills, column):
    """Rank jobs or courses based on TF-IDF similarity with user skills"""
    if df.empty:
        return df
    user_skills_str = " ".join(user_skills)
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df[column].tolist() + [user_skills_str])
    sim = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    df["Match %"] = (sim * 100).round(1)
    return df.sort_values(by="Match %", ascending=False)

# =======================
# Main app logic
# =======================
if st.button("Find Opportunities"):

    if not user_input.strip():
        st.warning("Please enter at least one skill.")
    else:
        user_skills = [skill.strip() for skill in user_input.split(",")]
        
        # Fetch jobs & courses
        st.info("Fetching jobs...")
        jobs_df = fetch_jobs(user_skills)
        st.info("Fetching courses...")
        courses_df = fetch_courses(user_skills)
        
        # Rank by similarity
        jobs_df = rank_similarity(jobs_df, user_skills, "Description")
        courses_df = rank_similarity(courses_df, user_skills, "Description")
        
        # Display results
        st.subheader("📌 Recommended Jobs")
        if not jobs_df.empty:
            st.dataframe(jobs_df[["Job", "Company", "Match %"]].reset_index(drop=True), use_container_width=True)
        else:
            st.write("No jobs found for these skills.")
        
        st.subheader("📚 Recommended Courses")
        if not courses_df.empty:
            st.dataframe(courses_df[["Course", "URL", "Match %"]].reset_index(drop=True), use_container_width=True)
        else:
            st.write("No courses found for these skills.")
