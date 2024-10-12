from flask import Flask, jsonify, request
from flask_cors import CORS
from main import rank_resumes, jd_collection, get_job_description, add_JD_tags
from io import BytesIO
import json

default_weights = {
    "education": 0.15,
    "work_experience": 0.30,
    "skills": 0.25,
    "certifications": 0.10,
    "projects": 0.10,
    "additional_info": 0.10
}


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Home Route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Resume Parser"})

# Resume Routes
@app.route('/resumes', methods=['POST'])
def upload_resumes():
    files = request.files.getlist('resumes')  # Get the list of uploaded files
    ranked_resumes = rank_resumes(files, default_weights)
    return jsonify({"message": "Resumes evaluated", "results": ranked_resumes}), 200

# JD Routes
@app.route('/jd', methods=['POST'])
def create_job_description():
    files = request.files.getlist('jds')
    for file in files:
        add_JD_tags(BytesIO(file.read()))
    return jsonify({"message": "Job descriptions created successfully!"}), 201

# Other JD routes remain unchanged

# Example route to retrieve resume scores
@app.route('/resumes/scores', methods=['POST'])
def get_resume_scores():
    files = request.files.getlist('resumes')
    with open('weights.json', 'r') as f:
        weights = json.load(f)
    
    ranked_resumes = rank_resumes(files, weights)
    return jsonify({"message": "Resume scores retrieved", "results": ranked_resumes}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)