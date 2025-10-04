import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =======================
# Sample Datasets
# =======================
jobs = pd.DataFrame({
    "Job": ["Data Analyst", "Machine Learning Engineer", "Web Developer", "Cybersecurity Specialist"],
    "Required_Skills": [
        "Python SQL Excel",
        "Python TensorFlow PyTorch MachineLearning",
        "HTML CSS JavaScript React",
        "Networking Security Python Linux"
    ]
})

headers = {
    "X-RapidAPI-Key": st.secrets["RAPIDAPI_KEY"],
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

courses = pd.DataFrame({
    "Course": ["Intro to Python Programming", "Machine Learning with TensorFlow", 
               "Web Development Bootcamp", "Cybersecurity Fundamentals"],
    "Teaches_Skills": [
        "Python Basics SQL",
        "Python TensorFlow MachineLearning",
        "HTML CSS JavaScript React",
        "Networking Security Linux"
    ]
})

# =======================
# Recommendation Function
# =======================
def recommend(user_skills):
    user_skills_str = " ".join(user_skills)
    vectorizer = TfidfVectorizer()
    
    # Jobs
    job_vectors = vectorizer.fit_transform(jobs["Required_Skills"].tolist() + [user_skills_str])
    job_sim = cosine_similarity(job_vectors[-1], job_vectors[:-1]).flatten()
    jobs["Match %"] = (job_sim * 100).round(1)
    
    # Courses
    course_vectors = vectorizer.fit_transform(courses["Teaches_Skills"].tolist() + [user_skills_str])
    course_sim = cosine_similarity(course_vectors[-1], course_vectors[:-1]).flatten()
    courses["Match %"] = (course_sim * 100).round(1)
    
    return jobs.sort_values(by="Match %", ascending=False), courses.sort_values(by="Match %", ascending=False)

# =======================
# Streamlit UI
# =======================
st.set_page_config(page_title="AI Job & Course Finder", page_icon="💼", layout="wide")

st.title("💼 AI Job & Course Finder")
st.write("Enter your skills and get personalized job & course recommendations!")
st.write("Your API key is:", st.secrets["RAPIDAPI_KEY"])
user_input = st.text_input("Enter your skills (comma separated):", "Python, SQL")

if st.button("Find Opportunities"):
    if user_input.strip():
        user_skills = [skill.strip() for skill in user_input.split(",")]
        job_recs, course_recs = recommend(user_skills)
        
        st.subheader("📌 Recommended Jobs")
        st.dataframe(job_recs[["Job", "Match %"]].reset_index(drop=True), use_container_width=True)
        
        st.subheader("📚 Recommended Courses")
        st.dataframe(course_recs[["Course", "Match %"]].reset_index(drop=True), use_container_width=True)
    else:
        st.warning("Please enter at least one skill.")


