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
@app.route('/upload_resumes', methods=['POST'])
def upload_resume():
    files = request.files.getlist('resumes')  # Get the list of uploaded files

    if not os.path.exists(EMPLOYEE_FOLDER):
        os.makedirs(EMPLOYEE_FOLDER)

    for file in files:
        file.save(f"{EMPLOYEE_FOLDER}/{file.filename}")  # Save each uploaded resume

    return jsonify({"message": "Resumes uploaded successfully!"}), 200

# API to delete an uploaded resume
@app.route('/delete_resumes', methods=['DELETE'])
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

# API to create a job description with separate categories
@app.route('/create_JDs', methods=['POST'])
def create_job_description():
    new_job_description = request.json

    # Iterate through each category and insert separately
    for category, keywords in new_job_description.items():        
        jd_collection.insert_one({"category": category, "data": keywords})  # Insert each category as a separate document

    return jsonify({"message": "Job descriptions created successfully!"}), 201

# API to create tags with separate categories
@app.route('/create_tags', methods=['POST'])
def create_tag():
    new_tag = request.json
    # Iterate through each category and insert separately
    for category, tags in new_tag.items():
        tags_collection.insert_one({"category": category, "data": tags})
    return jsonify({"message": "Tags added successfully"}), 201

# API to update a job description
@app.route('/update_JDs', methods=['PUT'])
def update_job_description():
    updated_job_description = request.json
    job_title = updated_job_description.get("job_title")
    result = jd_collection.update_one({"job_title": job_title}, {"$set": updated_job_description})
    if result.matched_count:
        return jsonify({"message": "Job description updated successfully!"}), 200
    else:
        return jsonify({"error": "Job title not found!"}), 404
    
# API to update a tag
@app.route('/update_subtags', methods=['PUT'])
def update_tag():
    old_tag = updated_tag.get("filter")
    updated_tag = request.json.get('update')
    result = tags_collection.update_one(old_tag, {"$set": updated_tag})
    if result.matched_count:
        return jsonify({"message": "Tag updated successfully!"}), 200
    else:
        return jsonify({"error": "Tag not found!"}), 404

# API to append multiple JDs to a category
@app.route('/sub_jds', methods=['POST'])
def append_jds():
    request_data = request.json
    category = request_data.get("category")
    new_jds = request_data.get("jds")  # Expecting a list of JDs

    # Find the JD category
    jd_entry = jd_collection.find_one({"category": category})

    if jd_entry:
        # Append new JDs to the data list
        existing_jds = jd_entry["data"]

        # Add only those JDs which are not already present
        for jd in new_jds:
            if jd not in existing_jds:
                existing_jds.append(jd)

        # Update the database
        jd_collection.update_one(
            {"category": category},
            {"$set": {"data": existing_jds}}
        )
        return jsonify({"message": "JDs appended successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404


# API to append multiple tags to a subcategory
@app.route('/sub_tags', methods=['POST'])
def append_tags():
    request_data = request.json
    category = request_data.get("category")
    subcategory = request_data.get("subcategory")
    new_tags = request_data.get("tags")  # Expecting a list of tags

    # Find the category
    tag_entry = tags_collection.find_one({"category": category})

    if tag_entry:
        # Append the new tags to the subcategory's tag list
        if subcategory in tag_entry["data"]:
            existing_tags = tag_entry["data"][subcategory]

            # Add only those tags which are not already present
            for tag in new_tags:
                if tag not in existing_tags:
                    existing_tags.append(tag)

            # Update the database
            tags_collection.update_one(
                {"category": category},
                {"$set": {f"data.{subcategory}": existing_tags}}
            )
            return jsonify({"message": "Tags appended successfully!"}), 200
        else:
            return jsonify({"error": "Subcategory not found!"}), 404
    else:
        return jsonify({"error": "Category not found!"}), 404


# API to remove multiple JDs from a category
@app.route('/sub_jds', methods=['DELETE'])
def remove_jds():
    request_data = request.json
    category = request_data.get("category")
    jds_to_remove = request_data.get("jds")  # Expecting a list of JDs

    # Find the JD category
    jd_entry = jd_collection.find_one({"category": category})

    if jd_entry:
        # Check if the JDs exist in the category
        existing_jds = jd_entry["data"]

        # Remove only those JDs which are present
        for jd in jds_to_remove:
            if jd in existing_jds:
                existing_jds.remove(jd)

        # Update the database
        jd_collection.update_one(
            {"category": category},
            {"$set": {"data": existing_jds}}
        )
        return jsonify({"message": "JDs removed successfully!"}), 200
    else:
        return jsonify({"error": "Category not found!"}), 404

# API to remove multiple tags from a subcategory
@app.route('/sub_tags', methods=['DELETE'])
def remove_tags():
    request_data = request.json
    category = request_data.get("category")
    subcategory = request_data.get("subcategory")
    tags_to_remove = request_data.get("tags")  # Expecting a list of tags

    # Find the category
    tag_entry = tags_collection.find_one({"category": category})

    if tag_entry:
        # Check if the subcategory exists
        if subcategory in tag_entry["data"]:
            existing_tags = tag_entry["data"][subcategory]

            # Remove only those tags which are present
            for tag in tags_to_remove:
                if tag in existing_tags:
                    existing_tags.remove(tag)

            # Update the database
            tags_collection.update_one(
                {"category": category},
                {"$set": {f"data.{subcategory}": existing_tags}}
            )
            return jsonify({"message": "Tags removed successfully!"}), 200
        else:
            return jsonify({"error": "Subcategory not found!"}), 404
    else:
        return jsonify({"error": "Category not found!"}), 404


# API to delete a job description
@app.route('/delete_JD', methods=['DELETE'])
def delete_job_description():
    job_title = request.json.get("job_title")
    result = jd_collection.delete_one({"job_title": job_title})
    if result.deleted_count:
        return jsonify({"message": "Job description deleted successfully!"}), 200
    else:
        return jsonify({"error": "Job title not found!"}), 404

## FIX THIS TING
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
    return jsonify({"JDs": job_descriptions})

# API to get all tags
@app.route('/get_all_tags', methods=['GET'])
def get_tags():
    tags = list(tags_collection.find({}, {"_id": 0}))  # Get all tags without MongoDB's internal _id field
    return jsonify({"tags": tags})

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