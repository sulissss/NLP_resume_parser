import json
import os
import shutil
from flask_cors import CORS
from flask import Flask, request, jsonify
from main_llm import jd_collection, add_JD_tags, rank_resumes

# Initialize Flask app
app = Flask(__name__)
EMPLOYEE_FOLDER = "employees"
JD_FOLDER = "JD"

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
    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)
    for file in files:
        file.save(f"{EMPLOYEE_FOLDER}/{file.filename}")  # Save each uploaded resume
    return jsonify({"message": "Resumes uploaded successfully!"}), 200

@app.route('/resumes', methods=['DELETE'])
def delete_resumes():
    file_names = request.json.get("resumes")
    for file_name in file_names:
        total_file_path = f"{EMPLOYEE_FOLDER}/{file_name}"
        if os.path.exists(total_file_path):
            os.remove(total_file_path)         
        else:
            return jsonify({"error": "File not found!"}), 404
    return jsonify({"message": "Resumes deleted successfully!"}), 200

@app.route('/resumes/all', methods=['DELETE'])
def delete_all_resumes():
    if os.path.exists(EMPLOYEE_FOLDER):
        shutil.rmtree(EMPLOYEE_FOLDER)  # Remove directory and contents
    os.makedirs(EMPLOYEE_FOLDER)  # Recreate directory
    return jsonify({"message": "All Resumes deleted successfully!"}), 200

@app.route('/resumes/scores', methods=['GET'])
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
    
# JD Routes
@app.route('/jd', methods=['POST'])
def upload_jds():
    files = request.files.getlist('jds')  # Get the list of uploaded files
    if not os.path.exists(JD_FOLDER):
        os.makedirs(JD_FOLDER)
    for file in files:
        jd_path = f"{JD_FOLDER}/{file.filename}"
        file.save(jd_path)  # Save each uploaded resume
        add_JD_tags(jd_path)
    return jsonify({"message": "JDs uploaded successfully!"}), 200

# @app.route('/jd', methods=['PUT'])
# def update_job_description():
#     updated_job_description = request.json
#     category = updated_job_description.get("category")
#     result = jd_collection.update_one({"category": category}, {"$set": updated_job_description})
#     if result.matched_count:
#         return jsonify({"message": "Job description updated successfully!"}), 200
#     else:
#         return jsonify({"error": "Category not found!"}), 404

@app.route('/jd', methods=['DELETE'])
def delete_job_description():
    category = request.json.get("category")
    result = jd_collection.delete_one({"category": category})
    if result.deleted_count:
        return jsonify({"message": "Job description deleted successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404

@app.route('/jd/all', methods=['GET'])
def get_job_descriptions():
    job_descriptions = list(jd_collection.find({}, {"_id": 0}))
    return jsonify({"JDs": job_descriptions})

@app.route('/jd/all', methods=['DELETE'])
def delete_all_job_descriptions():
    jd_collection.delete_many({})
    return jsonify({"message": "All job descriptions deleted successfully!"}), 200

# @app.route('/jd/sub', methods=['POST'])
# def append_jds():
#     request_data = request.json
#     category = request_data.get("category")
#     new_jds = request_data.get("jds")

#     jd_entry = jd_collection.find_one({"category": category})

#     if jd_entry:
#         existing_jds = jd_entry["data"]
#         for jd in new_jds:
#             if jd not in existing_jds:
#                 existing_jds.append(jd)

#         jd_collection.update_one(
#             {"category": category},
#             {"$set": {"data": existing_jds}}
#         )
#         return jsonify({"message": "JDs appended successfully!"}), 200
#     else:
#         return jsonify({"error": "Category not found!"}), 404

# @app.route('/jd/sub', methods=['DELETE'])
# def remove_jds():
#     request_data = request.json
#     category = request_data.get("category")
#     jds_to_remove = request_data.get("jds")

#     jd_entry = jd_collection.find_one({"category": category})

#     if jd_entry:
#         existing_jds = jd_entry["data"]
#         for jd in jds_to_remove:
#             if jd in existing_jds:
#                 existing_jds.remove(jd)

#         jd_collection.update_one(
#             {"category": category},
#             {"$set": {"data": existing_jds}}
#         )
#         return jsonify({"message": "JDs removed successfully!"}), 200
#     else:
#         return jsonify({"error": "Category not found!"}), 404

# @app.route('/jd/<string:category>', methods=['GET'])
# def get_job_description_by_category(category):
#     jd_entry = jd_collection.find_one({"category": category}, {"_id": 0})
#     if jd_entry:
#         return jsonify(jd_entry), 200
#     else:
#         return jsonify({"error": "Category not found!"}), 404

# Weights Routes
@app.route('/weights', methods=['POST'])
def set_weights():
    weights_data = request.json
    with open('weights.json', 'w') as f:
        json.dump(weights_data, f)
    return jsonify({"message": "Weights set successfully!"}), 200

@app.route('/weights', methods=['GET'])
def get_weights():
    if os.path.exists('weights.json'):
        with open('weights.json', 'r') as f:
            weights = json.load(f)
        return jsonify(weights), 200
    else:
        return jsonify({"error": "Weights file not found!"}), 404


if __name__ == '__main__':
    app.run(port=5001, debug=True)