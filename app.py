from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import shutil
import json
from nlp_spacy import rank_resumes
from pymongo import MongoClient

EMPLOYEE_FOLDER = "employees"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

client = MongoClient("mongodb://localhost:27017/")
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions
tags_collection = db["tags"]  # Collection for Tags

# jd_collection.delete_many({'eee': 'aaa'})


# for x in jd_collection.find():
#     print(x)

# print(jd_collection.find({"description": "Develops and maintains software applications."}))

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "yoo wassup"})

# API to upload resumes
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    file_paths = request.files['resumes']
    
    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)

    for file_path in file_paths:
        file_paths.save(f"{EMPLOYEE_FOLDER}/{file_paths.filename}")  # Save uploaded resume
    return jsonify({"message": "Resume uploaded successfully!"}), 200


# API to delete an uploaded resume
@app.route('/delete_resume', methods=['DELETE'])
def delete_resume():
    file_names = request.json.get("resumes")
    for file_name in file_names:
        total_file_path = f"{EMPLOYEE_FOLDER}/{file_name}"
        if os.path.exists(total_file_path):
            shutil.rmtree(total_file_path)         
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
@app.route('/create_job_description', methods=['POST'])
def create_job_description():
    new_jds = request.json
    if not isinstance(new_jds, list):
        new_jds = [new_jds]
    jd_collection.insert_many(new_jds)
    return jsonify({"message": "Job description created successfully!"}), 201

# API to update a job description
@app.route('/update_job_description', methods=['PUT'])
def update_job_description():
    old_jd = request.json.get('filter')
    updated_jd = request.json.get('update')
    jd_collection.update_one(old_jd, {'$set': updated_jd})
    return jsonify({"message": "Job description updated successfully!"}), 200

# API to delete a job description
@app.route('/delete_job_description', methods=['DELETE'])
def delete_job_description():
    jd = request.json
    if jd_collection.delete_one(jd):
        return jsonify({"message": "Job description deleted successfully!"}), 200
    else:
        return jsonify({"message": "Job title not found!"}), 404

# API to create a tag
@app.route('/create_tag', methods=['POST'])
def create_tag():
    new_tags = request.json
    if not isinstance(new_tags, list):
        new_tags = [new_tags]
    tags_collection.insert_many(new_tags)
    return jsonify({"message": "Tag created successfully!"}), 201

# API to update a tag
@app.route('/update_tag', methods=['PUT'])
def update_tag():
    old_tag = request.json.get('filter')
    updated_tag = request.json.get('update')
    jd_collection.update_one(old_tag, {'$set': updated_tag})
    return jsonify({"message": "Tag updated successfully!"}), 200

# API to create a weight
@app.route('/create_weight', methods=['POST'])
def create_weight():
    new_weight = request.json
    with open('weights.json', 'r+') as f:
        data = json.load(f)
        data.update(new_weight)
        f.seek(0)
        json.dump(data, f, indent=4)
    return jsonify({"message": "Weight created successfully!"}), 201

# API to update a weight
@app.route('/update_weight', methods=['PUT'])
def update_weight():
    updated_weight = request.json
    with open('weights.json', 'r+') as f:
        data = json.load(f)
        data.update(updated_weight)
        f.seek(0)
        json.dump(data, f, indent=4)
    return jsonify({"message": "Weight updated successfully!"}), 200

@app.route('/get_resume_scores', methods=['GET'])
def get_resume_scores():
    
    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)

    file_paths = [f"{EMPLOYEE_FOLDER}/{file_path}" for file_path in os.listdir(EMPLOYEE_FOLDER)]
    
    if not file_paths:
        return jsonify({"error": "No resumes uploaded"})
    else:
        with open('JD.json', 'r') as f:
            job_description = json.load(f)
        with open('weights.json', 'r') as f:
            weights = json.load(f)
        with open('tags.json', 'r') as f:
            tags = json.load(f)

        return jsonify({"message": rank_resumes(file_paths, job_description, weights, tags)})



if __name__ == '__main__':
    app.run(port=5001, debug=True)