from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
import os
import shutil
import json
from nlp_spacy import rank_resumes, jd_collection, tags_collection

EMPLOYEE_FOLDER = "employees"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Blueprints
resume_bp = Blueprint('resume', __name__)
jd_bp = Blueprint('jd', __name__)
tag_bp = Blueprint('tag', __name__)
subjd_bp = Blueprint('subjd', __name__)
subtag_bp = Blueprint('subtag', __name__)
weights_bp = Blueprint('weights', __name__)

# Home Route
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Resume Parser"})

# Resume Routes
@resume_bp.route('/upload', methods=['POST'])
def upload_resumes():
    files = request.files.getlist('resumes')  # Get the list of uploaded files
    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)
    for file in files:
        file.save(f"{EMPLOYEE_FOLDER}/{file.filename}")  # Save each uploaded resume
    return jsonify({"message": "Resumes uploaded successfully!"}), 200

@resume_bp.route('/remove', methods=['DELETE'])
def delete_resumes():
    file_names = request.json.get("resumes")
    for file_name in file_names:
        total_file_path = f"{EMPLOYEE_FOLDER}/{file_name}"
        if os.path.exists(total_file_path):
            os.remove(total_file_path)         
        else:
            return jsonify({"error": "File not found!"}), 404
    return jsonify({"message": "Resumes deleted successfully!"}), 200


@resume_bp.route('/remove_all', methods=['DELETE'])
def delete_all_resumes():
    if os.path.exists(EMPLOYEE_FOLDER):
        shutil.rmtree(EMPLOYEE_FOLDER)  # Remove directory and contents
    os.makedirs(EMPLOYEE_FOLDER)  # Recreate directory
    return jsonify({"message": "All Resumes deleted successfully!"}), 200

@resume_bp.route('/get_scores', methods=['GET'])
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
@jd_bp.route('/create', methods=['POST'])
def create_job_description():
    new_job_description = request.json
    for category, keywords in new_job_description.items():
        jd_collection.insert_one({"category": category, "data": keywords})
    return jsonify({"message": "Job descriptions created successfully!"}), 201

@jd_bp.route('/update', methods=['PUT'])
def update_job_description():
    updated_job_description = request.json
    category = updated_job_description.get("category")
    result = jd_collection.update_one({"category": category}, {"$set": updated_job_description})
    if result.matched_count:
        return jsonify({"message": "Job description updated successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404

@jd_bp.route('/delete', methods=['DELETE'])
def delete_job_description():
    category = request.json.get("category")
    result = jd_collection.delete_one({"category": category})
    if result.deleted_count:
        return jsonify({"message": "Job description deleted successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404

@jd_bp.route('/get_all', methods=['GET'])
def get_job_descriptions():
    job_descriptions = list(jd_collection.find({}, {"_id": 0}))
    return jsonify({"JDs": job_descriptions})

@jd_bp.route('/delete_all', methods=['DELETE'])
def delete_all_job_descriptions():
    jd_collection.delete_many({})
    return jsonify({"message": "All job descriptions deleted successfully!"}), 200

# Tag Routes
@tag_bp.route('/create', methods=['POST'])
def create_tags():
    new_tag = request.json
    for category, tags in new_tag.items():
        tags_collection.insert_one({"category": category, "data": tags})
    return jsonify({"message": "Tags added successfully"}), 201

@tag_bp.route('/update', methods=['PUT'])
def update_tag():
    updated_tag = request.json
    old_tag = updated_tag.get("filter")
    new_tag_data = updated_tag.get("update")
    result = tags_collection.update_one(old_tag, {"$set": new_tag_data})
    if result.matched_count:
        return jsonify({"message": "Tag updated successfully!"}), 200
    else:
        return jsonify({"error": "Tag not found!"}), 404

@tag_bp.route('/delete', methods=['DELETE'])
def delete_tag():
    tag_name = request.json.get("tag_name")
    result = tags_collection.delete_one({"category": tag_name})  # Use "category" based on your structure
    if result.deleted_count:
        return jsonify({"message": "Tag deleted successfully!"}), 200
    else:
        return jsonify({"error": "Tag not found!"}), 404

@tag_bp.route('/get_all', methods=['GET'])
def get_tags():
    tags = list(tags_collection.find({}, {"_id": 0}))
    return jsonify({"tags": tags})

@tag_bp.route('/delete_all', methods=['DELETE'])
def delete_all_tags():
    tags_collection.delete_many({})
    return jsonify({"message": "All tags deleted successfully!"}), 200

# Sub JD Blueprint
@subjd_bp.route('/sub_jds', methods=['POST'])
def append_jds():
    request_data = request.json
    category = request_data.get("category")
    new_jds = request_data.get("jds")

    jd_entry = jd_collection.find_one({"category": category})

    if jd_entry:
        existing_jds = jd_entry["data"]
        for jd in new_jds:
            if jd not in existing_jds:
                existing_jds.append(jd)

        jd_collection.update_one(
            {"category": category},
            {"$set": {"data": existing_jds}}
        )
        return jsonify({"message": "JDs appended successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404

@subjd_bp.route('/sub_jds', methods=['DELETE'])
def remove_jds():
    request_data = request.json
    category = request_data.get("category")
    jds_to_remove = request_data.get("jds")

    jd_entry = jd_collection.find_one({"category": category})

    if jd_entry:
        existing_jds = jd_entry["data"]
        for jd in jds_to_remove:
            if jd in existing_jds:
                existing_jds.remove(jd)

        jd_collection.update_one(
            {"category": category},
            {"$set": {"data": existing_jds}}
        )
        return jsonify({"message": "JDs removed successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404

# Subtag Blueprint
@subtag_bp.route('/sub_tags', methods=['POST'])
def append_tags():
    request_data = request.json
    category = request_data.get("category")
    subcategory = request_data.get("subcategory")
    new_tags = request_data.get("tags")

    tag_entry = tags_collection.find_one({"category": category})

    if tag_entry:
        if subcategory in tag_entry["data"]:
            existing_tags = tag_entry["data"][subcategory]
            for tag in new_tags:
                if tag not in existing_tags:
                    existing_tags.append(tag)

            tags_collection.update_one(
                {"category": category},
                {"$set": {f"data.{subcategory}": existing_tags}}
            )
            return jsonify({"message": "Tags appended successfully!"}), 200
        else:
            return jsonify({"error": "Subcategory not found!"}), 404
    else:
        return jsonify({"error": "Category not found!"}), 404

@subtag_bp.route('/sub_tags', methods=['DELETE'])
def remove_tags():
    request_data = request.json
    category = request_data.get("category")
    subcategory = request_data.get("subcategory")
    tags_to_remove = request_data.get("tags")

    tag_entry = tags_collection.find_one({"category": category})

    if tag_entry:
        if subcategory in tag_entry["data"]:
            existing_tags = tag_entry["data"][subcategory]
            for tag in tags_to_remove:
                if tag in existing_tags:
                    existing_tags.remove(tag)

            tags_collection.update_one(
                {"category": category},
                {"$set": {f"data.{subcategory}": existing_tags}}
            )
            return jsonify({"message": "Tags removed successfully!"}), 200
        else:
            return jsonify({"error": "Subcategory not found!"}), 404
    else:
        return jsonify({"error": "Category not found!"}), 404

# Weights Blueprint
@weights_bp.route('/set_weights', methods=['POST'])
def set_weights():
    weights_data = request.json
    with open('weights.json', 'w') as f:
        json.dump(weights_data, f)
    return jsonify({"message": "Weights set successfully!"}), 200

@weights_bp.route('/get_weights', methods=['GET'])
def get_weights():
    if os.path.exists('weights.json'):
        with open('weights.json', 'r') as f:
            weights = json.load(f)
        return jsonify(weights), 200
    else:
        return jsonify({"error": "Weights file not found!"}), 404


# Register blueprints with the Flask app
app.register_blueprint(resume_bp, url_prefix='/resume')
app.register_blueprint(jd_bp, url_prefix='/jd')
app.register_blueprint(subjd_bp, url_prefix='/subjd')
app.register_blueprint(tag_bp, url_prefix='/tag')
app.register_blueprint(subtag_bp, url_prefix='/subtag')
app.register_blueprint(weights_bp, url_prefix='/weights')

if __name__ == '__main__':
    app.run(port=5001, debug=True)