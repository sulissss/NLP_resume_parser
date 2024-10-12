import json
import re
import os
import spacy
from dotenv import load_dotenv
from io import BytesIO
from pymongo import MongoClient
from utils import parse_resume
from llm import get_JD_tags, assess_candidate, resume_or_not

load_dotenv('mongo.env')

# MongoDB setup
client = MongoClient(os.getenv('MONGODB_URI'))
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions

nlp = spacy.load("en_core_web_sm")

def get_job_description():
    jd_docs = list(jd_collection.find({}))
    return {doc['category']: doc['data'] for doc in jd_docs}

def add_JD_tags(JD_text):
    tags_and_reqs = get_JD_tags(JD_text)

    # Add tags to the tags collection uniquely
    for category, tags in tags_and_reqs.items():
        modified_tags = [tag.lower().replace('_', ' ') for tag in tags]
        jd_collection.update_one(
            {"category": category},  # Ensure correct category
            {"$addToSet": {"data": {"$each": modified_tags}}},  # Add tags only if they are not already present
            upsert=True  # Insert new category if it doesn't exist
        )

def calculate_score(resume_text, weights):
    total_score = 0
    
    # Normalize the resume text
    resume_text = " ".join([token.text.lower() for token in nlp(resume_text) if not token.is_space and not token.is_punct])
    
    # Retrieve all job descriptions
    job_descriptions = get_job_description()
    
    # Iterate through each category and calculate the score
    for category, weight in weights.items():
        keywords = job_descriptions.get(category, [])
        match_indicator = 1 if any(re.search(rf'\b{keyword}\b', resume_text, re.IGNORECASE) for keyword in keywords) else 0
        total_score += (weight * match_indicator)  # Sum the weighted scores

    return total_score  # Return total score without normalization


def rank_resumes(resume_files, weights, JD_check=False, include_fit=False):
    """
    Modify rank_resumes to work with in-memory files.
    """
    ranked_resumes = []
    for resume_file in resume_files:
        resume_text = parse_resume(BytesIO(resume_file.read()), resume_file.filename)
        if JD_check:
            if not resume_or_not(resume_text)['is_resume']:
                add_JD_tags(resume_text)
                ranked_resumes.append((resume_file.filename, "JD file"))
                continue
        candidate_is_fit = True
        if include_fit:
            job_description = get_job_description()
            inferenced_resume = assess_candidate(job_description, resume_text)
            candidate_is_fit = inferenced_resume['is_fit']
        if candidate_is_fit:
            score = calculate_score(resume_text, weights)
            ranked_resumes.append((resume_file.filename, score))
        else:
            ranked_resumes.append((resume_file.filename, inferenced_resume['reasoning']))

    return ranked_resumes