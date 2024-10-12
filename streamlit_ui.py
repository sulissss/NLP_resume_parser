import streamlit as st
import os
import requests
import json
import requests
from main import rank_resumes, get_job_description, add_JD_tags

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


st.header("Make an API call")

# Dropdown for selecting HTTP method
http_method = st.selectbox("Select HTTP Method", ["GET", "POST", "PUT", "DELETE"])

# Input box for entering the URL
url = st.text_input("Enter API URL", "http://127.0.0.1:5001/")  # You can provide a default URL for convenience

# If the method is POST, provide additional input for data
if http_method in ["POST", "PUT"]:
    data = st.text_area("Enter Data (JSON format)", '{"key": "value"}')  # JSON format by default

# Button to make the request
if st.button("Send"):
    try:
        # Prepare the request based on the selected method
        if http_method == "GET":
            response = requests.get(url)
        elif http_method == "POST":
            response = requests.post(url, json=json.loads(data))
        elif http_method == "PUT":
            response = requests.put(url, json=json.loads(data))
        elif http_method == "DELETE":
            response = requests.delete(url)
        
        # Display the response
        st.write("Response Status Code:", response.status_code)
        st.write("Response Body:")
        st.json(response.json())  # Display the response as JSON if possible
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
    except json.JSONDecodeError:
        st.error("Invalid JSON format in data.")


# --- Section for Uploading Resumes ---
st.header("Upload Files (Resumes or Job Description)")
uploaded_resume_files = st.file_uploader("Upload Files", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="resume_uploader")

if uploaded_resume_files:
    st.write(f"Saving {len(uploaded_resume_files)} file(s) locally...")
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
if st.button("Evaluate Resumes and JDs") and uploaded_resume_files:
    # Rank resumes based on the adjusted weights
    st.write("Evaluating Resumes and JDs...")
    ranked_resumes = rank_resumes(resume_paths, default_weights, JD_check=True)
    
    # Display the results
    st.header("Resume Scores")
    for resume in ranked_resumes:
        is_fit = True
        resume_path, score_or_reason = resume
        if score_or_reason == "JD file":
            st.markdown(f"{resume_path} is a JD file")
            continue
        st.write(f"Resume: {os.path.basename(resume_path)}")
        if is_fit:
            st.markdown(f"<h2 style='color:green;'>Score: {score_or_reason}</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color:red;'>Not a Fit: {score_or_reason}</h2>", unsafe_allow_html=True)