import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient
from llm import get_JD_tags, assess_candidate, resume_or_not

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
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

def rank_resumes(resume_paths, weights, JD_check=False, include_fit=False):
    ranked_resumes = []
    for resume_path in resume_paths:
        resume_text = parse_resume(resume_path)
        if JD_check:
            if not resume_or_not(resume_text)['is_resume']:
                add_JD_tags(resume_text)
                ranked_resumes.append((resume_path, "JD file"))
                continue
        candidate_is_fit = True
        if include_fit:
            job_description = get_job_description()
            inferenced_resume = assess_candidate(job_description, resume_text)
            candidate_is_fit = inferenced_resume['is_fit']
        if candidate_is_fit:
            score = calculate_score(resume_text, weights)
            ranked_resumes.append((resume_path, score))
        else:
            ranked_resumes.append((resume_path, inferenced_resume['reasoning']))

    return ranked_resumes

default_weights = {
    "education": 0.15,
    "work_experience": 0.30,
    "skills": 0.25,
    "certifications": 0.10,
    "projects": 0.10,
    "additional_info": 0.10
}

# Example usage
# print(rank_resumes(['/Users/sulaiman/Downloads/Gokul_Raj (1).pdf', '/Users/sulaiman/Downloads/RIYAZUDDIN_SHAIKH (1).pdf'], default_weights))
# print(rank_resumes(['/Applications/Documents/Tags, Ranking and Sample CVs/Sample CVs/Muhammed_Favas_AK.pdf'], default_weights))