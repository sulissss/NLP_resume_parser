import streamlit as st
import os
from io import BytesIO
from main_llm import rank_resumes, add_JD_tags, get_job_description  # Assuming these are in your main code
import json

# Local directory to save resumes and JDs
UPLOAD_FOLDER = "uploaded_resumes"
JD_FOLDER = "uploaded_jds"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(JD_FOLDER):
    os.makedirs(JD_FOLDER)

# Default weights for evaluation
default_weights = {
    "education": 0.15,
    "work_experience": 0.30,
    "skills": 0.25,
    "certifications": 0.10,
    "projects": 0.10,
    "additional_info": 0.10
}

# Streamlit App
st.title("Resume and JD Upload and Evaluation System")

# --- Section for Uploading Job Descriptions (JDs) ---
st.header("Upload Job Descriptions")
uploaded_jd_files = st.file_uploader("Upload JD Files", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="jd_uploader")

if uploaded_jd_files:
    st.write(f"Saving {len(uploaded_jd_files)} JD(s) locally...")
    jd_paths = []
    
    # Save each uploaded JD locally
    for jd_file in uploaded_jd_files:
        file_name = jd_file.name
        save_path = os.path.join(JD_FOLDER, file_name)
        
        # Save JD file to disk
        with open(save_path, "wb") as f:
            f.write(jd_file.getbuffer())
        st.success(f"Saved JD {file_name} to {JD_FOLDER}")
        jd_paths.append(save_path)
        
        # Process JD and add tags to MongoDB
        add_JD_tags(save_path)

# --- Section for Viewing Job Descriptions ---
if st.button("Show All Job Descriptions"):
    st.header("Uploaded Job Descriptions")
    job_descriptions = get_job_description()
    if job_descriptions:
        for category, tags in job_descriptions.items():
            st.write(f"**Category**: {category}")
            st.write(f"**Tags**: {', '.join(tags)}")
    else:
        st.error("No job descriptions available.")

# --- Section for Uploading Resumes ---
st.header("Upload Resumes")
uploaded_resume_files = st.file_uploader("Upload Resume Files", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="resume_uploader")

if uploaded_resume_files:
    st.write(f"Saving {len(uploaded_resume_files)} resume(s) locally...")
    resume_paths = []
    
    # Save each uploaded resume locally
    for uploaded_file in uploaded_resume_files:
        file_name = uploaded_file.name
        save_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # Save resume file to disk
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved {file_name} to {UPLOAD_FOLDER}")
        resume_paths.append(save_path)

# --- Section for Adjusting Weights for Scoring ---
st.header("Adjust Weights for Evaluation")
weights = {
    "education": st.slider("Education Weight", 0.0, 1.0, default_weights["education"]),
    "work_experience": st.slider("Work Experience Weight", 0.0, 1.0, default_weights["work_experience"]),
    "skills": st.slider("Skills Weight", 0.0, 1.0, default_weights["skills"]),
    "projects": st.slider("Projects Weight", 0.0, 1.0, default_weights["projects"]),
    "certifications": st.slider("Certifications Weight", 0.0, 1.0, default_weights["certifications"]),
    "additional_info": st.slider("Additional Info Weight", 0.0, 1.0, default_weights["additional_info"])
}

# --- Section for Evaluating Resumes ---
if st.button("Evaluate Resumes") and uploaded_resume_files:
    # Rank resumes based on the adjusted weights
    st.write("Evaluating resumes...")
    ranked_resumes = rank_resumes(resume_paths, weights)
    
    # Display the results
    st.header("Resume Scores")
    for resume in ranked_resumes:
        resume_path, is_fit, score_or_reason = resume
        st.write(f"Resume: {os.path.basename(resume_path)}")
        if is_fit:
            st.markdown(f"<h2 style='color:green;'>Score: {score_or_reason:.2f}</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color:red;'>Not a Fit: {score_or_reason}</h2>", unsafe_allow_html=True)

# Run the app with: streamlit run app.py