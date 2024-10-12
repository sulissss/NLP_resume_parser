import streamlit as st
import requests
import json

# Flask API URL (Change to your deployed Flask server's URL)
API_URL = "http://127.0.0.1:5001"

# Default weights for evaluation
default_weights = {
    "education": 0.15,
    "work_experience": 0.30,
    "skills": 0.25,
    "certifications": 0.10,
    "projects": 0.10,
    "additional_info": 0.10
}

st.title("Resume and JD Upload and Evaluation System")

# --- Section for Uploading Job Descriptions (JDs) ---
st.header("Upload Job Descriptions")
uploaded_jd_files = st.file_uploader("Upload JD Files", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="jd_uploader")

if uploaded_jd_files:
    st.write(f"Uploading {len(uploaded_jd_files)} JD(s) to the server...")
    
    # Upload JD files via API
    files = [('jds', (file.name, file, file.type)) for file in uploaded_jd_files]
    
    response = requests.post(f"{API_URL}/jd", files=files)
    
    if response.status_code == 201:
        st.success("Job descriptions uploaded successfully!")
    else:
        st.error(f"Failed to upload JDs: {response.json().get('message', 'Unknown error')}")


# --- Section for Viewing Job Descriptions ---
if st.button("Show All Job Descriptions"):
    st.header("Uploaded Job Descriptions")
    
    response = requests.get(f"{API_URL}/jd/all")
    
    if response.status_code == 200:
        job_descriptions = response.json().get("JDs", {})
        for category, tags in job_descriptions.items():
            st.write(f"**Category**: {category}")
            st.write(f"**Tags**: {', '.join(tags)}")
    else:
        st.error(f"Failed to fetch job descriptions: {response.json().get('message', 'Unknown error')}")


# --- Section for Uploading Resumes ---
st.header("Upload Resumes for Evaluation")
uploaded_resume_files = st.file_uploader("Upload Resumes", accept_multiple_files=True, type=["pdf", "docx", "txt"], key="resume_uploader")

if uploaded_resume_files:
    st.write(f"Uploading {len(uploaded_resume_files)} resume(s) to the server...")
    
    # Prepare files for upload
    files = [('resumes', (file.name, file, file.type)) for file in uploaded_resume_files]
    
    response = requests.post(f"{API_URL}/resumes", files=files)
    
    if response.status_code == 200:
        st.success("Resumes uploaded and evaluated successfully!")
    else:
        st.error(f"Failed to upload resumes: {response.json().get('message', 'Unknown error')}")


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
    st.write("Evaluating Resumes...")
    
    # Post weights to API to set them
    response = requests.post(f"{API_URL}/weights", json=weights)
    
    if response.status_code == 200:
        # Fetch scores after setting the weights
        score_response = requests.post(f"{API_URL}/resumes/scores", files=files)
        if score_response.status_code == 200:
            ranked_resumes = score_response.json().get("results", [])
            st.header("Resume Scores")
            for resume in ranked_resumes:
                resume_name, score_or_reason = resume
                st.write(f"Resume: {resume_name}")
                if isinstance(score_or_reason, float):
                    st.markdown(f"<h2 style='color:green;'>Score: {score_or_reason:.2f}</h2>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h2 style='color:red;'>Not a Fit: {score_or_reason}</h2>", unsafe_allow_html=True)
        else:
            st.error(f"Failed to fetch resume scores: {score_response.json().get('message', 'Unknown error')}")
    else:
        st.error(f"Failed to set weights: {response.json().get('message', 'Unknown error')}")


# --- API Interaction Section ---
st.header("Make an API call")

# Dropdown for selecting HTTP method
http_method = st.selectbox("Select HTTP Method", ["GET", "POST", "PUT", "DELETE"])

# Input box for entering the URL
url = st.text_input("Enter API URL", f"{API_URL}/")  # You can provide a default URL for convenience

# If the method is POST, provide additional input for data
if http_method in ["POST", "PUT"]:
    data = st.text_area("Enter Data (JSON format)", '{"key": "value"}')  # JSON format by default

# Button to make the request
if st.button("Send API Request"):
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