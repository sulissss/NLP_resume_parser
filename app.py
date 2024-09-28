from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import shutil
import json
from nlp_spacy import rank_resumes, jd_collection, tags_collection


EMPLOYEE_FOLDER = "employees"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Resume Parser"})

# API to upload resumes
# API to upload multiple resumes
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    files = request.files.getlist('resumes')  # Get the list of uploaded files

    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)

    for file in files:
        file.save(f"{EMPLOYEE_FOLDER}/{file.filename}")  # Save each uploaded resume

    return jsonify({"message": "Resumes uploaded successfully!"}), 200

# API to delete an uploaded resume
@app.route('/delete_resume', methods=['DELETE'])
def delete_resume():
    file_names = request.json.get("resumes")
    for file_name in file_names:
        total_file_path = f"{EMPLOYEE_FOLDER}/{file_name}"
        if os.path.exists(total_file_path):
            os.remove(total_file_path)         
        else:
            return jsonify({"error": "File not found!"}), 404
    return jsonify({"message": "Resumes deleted successfully!"}), 200

# API to delete all resumes
@app.route('/delete_all_resumes', methods=['DELETE'])
def delete_all_resumes():
    if os.path.exists(EMPLOYEE_FOLDER):
        shutil.rmtree(EMPLOYEE_FOLDER)  # Use shutil.rmtree to remove the directory and its contents
    os.makedirs(EMPLOYEE_FOLDER)  # Recreate the directory
    return jsonify({"message": "All Resumes deleted successfully!"}), 200

# API to create a job description
@app.route('/create_JD', methods=['POST'])
def create_job_description():
    new_job_description = request.json
    if not isinstance(new_job_description, list):
        new_job_description = [new_job_description]
    jd_collection.insert_many(new_job_description)  # Insert into MongoDB
    return jsonify({"message": "Job description created successfully!"}), 201

# API to update a job description
@app.route('/update_JD', methods=['PUT'])
def update_job_description():
    updated_job_description = request.json
    job_title = updated_job_description.get("job_title")
    result = jd_collection.update_one({"job_title": job_title}, {"$set": updated_job_description})
    if result.matched_count:
        return jsonify({"message": "Job description updated successfully!"}), 200
    else:
        return jsonify({"error": "Job title not found!"}), 404

# API to delete a job description
@app.route('/delete_JD', methods=['DELETE'])
def delete_job_description():
    job_title = request.json.get("job_title")
    result = jd_collection.delete_one({"job_title": job_title})
    if result.deleted_count:
        return jsonify({"message": "Job description deleted successfully!"}), 200
    else:
        return jsonify({"error": "Job title not found!"}), 404

# API to create a tag
@app.route('/create_tag', methods=['POST'])
def create_tag():
    new_tag = request.json
    if not isinstance(new_tag, list):
        new_tag = [new_tag]
    tags_collection.insert_many(new_tag)  # Insert into MongoDB
    return jsonify({"message": "Tag created successfully!"}), 201

# API to update a tag
@app.route('/update_tag', methods=['PUT'])
def update_tag():
    updated_tag = request.json
    tag_name = updated_tag.get("tag_name")
    result = tags_collection.update_one({"tag_name": tag_name}, {"$set": updated_tag})
    if result.matched_count:
        return jsonify({"message": "Tag updated successfully!"}), 200
    else:
        return jsonify({"error": "Tag not found!"}), 404

# API to delete a tag
@app.route('/delete_tag', methods=['DELETE'])
def delete_tag():
    tag_name = request.json.get("tag_name")
    result = tags_collection.delete_one({"tag_name": tag_name})
    if result.deleted_count:
        return jsonify({"message": "Tag deleted successfully!"}), 200
    else:
        return jsonify({"error": "Tag not found!"}), 404

# API to get all job descriptions
@app.route('/get_all_JDs', methods=['GET'])
def get_job_descriptions():
    job_descriptions = list(jd_collection.find({}, {"_id": 0}))  # Get all JDs without MongoDB's internal _id field
    return jsonify({"job_descriptions": job_descriptions[0]})

# API to get all tags
@app.route('/get_all_tags', methods=['GET'])
def get_tags():
    tags = list(tags_collection.find({}, {"_id": 0}))  # Get all tags without MongoDB's internal _id field
    return jsonify({"tags": tags[0]})

# API to delete all job descriptions
@app.route('/delete_all_JDs', methods=['DELETE'])
def delete_all_job_descriptions():
    jd_collection.delete_many({})  # Remove all documents in the job_descriptions collection
    return jsonify({"message": "All job descriptions deleted successfully!"}), 200

# API to delete all tags
@app.route('/delete_all_tags', methods=['DELETE'])
def delete_all_tags():
    tags_collection.delete_many({})  # Remove all documents in the tags collection
    return jsonify({"message": "All tags deleted successfully!"}), 200

@app.route('/get_resume_scores', methods=['GET'])
def get_resume_scores():
    
    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)

    file_paths = [f"{EMPLOYEE_FOLDER}/{file_path}" for file_path in os.listdir(EMPLOYEE_FOLDER)]
    
    if not file_paths:
        return jsonify({"error": "No resumes uploaded"})
    else:
        with open('weights.json', 'r') as f:
            weights = json.load(f)

        return jsonify({"message": rank_resumes(file_paths, weights)})


if __name__ == '__main__':
    app.run(port=5001, debug=True)