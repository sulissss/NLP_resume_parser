import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient
from llm import get_JD_tags, assess_candidate

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions
tags_collection = db["tags"]  # Collection for Tags

nlp = spacy.load("en_core_web_sm")

def get_job_description():
    jd_docs = list(jd_collection.find({}))
    return {doc['category']: doc['data'] for doc in jd_docs}

def add_JD_tags(JD_path):
    JD_text = parse_resume(JD_path)
    tags_and_reqs = get_JD_tags(JD_text)

    # print(tags_and_reqs)
    # Add tags to the tags collection uniquely
    for category, tags in tags_and_reqs.items():
        # print(category, "->", tags)
        modified_tags = [tag.lower().replace('_', ' ') for tag in tags]
        jd_collection.update_one(
            {"category": category},  # Ensure correct category
            {"$addToSet": {"data": {"$each": modified_tags}}},  # Add tags only if they are not already present
            upsert=True  # Insert new category if it doesn't exist
        )

def keyword_matching(resume_text, category, keywords, weights):
    matches = 0
    # Check if keywords are directly in resume text
    for keyword in keywords:
        if re.search(rf'\b{keyword}\b', resume_text, re.IGNORECASE):
            matches += (1 * weights[category])
    return matches


def calculate_score(resume_text, weights):
    total_score = 0
    total_weight = sum(weights.values())
    # Normalize the resume text
    resume_text = " ".join([token.text.capitalize() for token in nlp(resume_text) if not token.is_space and not token.is_punct])
    
    # Retrieve all job descriptions
    job_descriptions = get_job_description()
    
    # Iterate through each job description document
    for category, keywords in job_descriptions.items():
        # Perform keyword matching for the current category
        keyword_matches = keyword_matching(resume_text, category, keywords, weights)
        max_matches = len(keywords)
        
        # Calculate weighted score for the category if there are keywords to match against
        if max_matches > 0 and category != 'job_requirements':
            score_for_category = (keyword_matches / max_matches) * weights[category]
            total_score += score_for_category

    # Normalize the total score by the total weights
    normalized_total_score = (total_score / total_weight) * 100  # To get a percentage value
    return normalized_total_score

def rank_resumes(resume_paths, weights):
    ranked_resumes = []
    for resume_path in resume_paths:
        resume_text = parse_resume(resume_path)
        job_description = get_job_description()
        inferenced_resume = assess_candidate(job_description, resume_text)
        if inferenced_resume['is_fit']:
            added_string = resume_text.split() + inferenced_resume['tags']
            print(" ".join(added_string))
            final_string = []
            for c in added_string:
                if c not in final_string:
                    final_string.append(c)
            final_string = " ".join(final_string)
            # resume_text = " ".join(list(set((" ".join(inferenced_resume['tags']) + resume_text).split())))
            print("\n\n\n-------------------\n\n\n")
            print(final_string)
            score = calculate_score(final_string, weights)
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

print(rank_resumes(['/Users/sulaiman/Downloads/Gokul_Raj (1).pdf'], default_weights))