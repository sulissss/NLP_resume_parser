import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient
from main_llm import get_job_description

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions
tags_collection = db["tags"]  # Collection for Tags

nlp = spacy.load("en_core_web_sm")

def keyword_matching(resume_text, category, keywords, weights):
    matches = 0
    # Check if keywords are directly in resume text
    for keyword in keywords:
        if re.search(rf'\b{keyword}\b', resume_text, re.IGNORECASE):
            matches += (1 * weights[category])
        else:
            # Retrieve synonyms from the tags collection for the current category
            synonyms = tags_collection.find_one({"category": category})
            if not synonyms:
                continue
            
            synonyms = synonyms['data']  # Access nested 'data' structure

            if keyword in synonyms:
                for synonym in synonyms[keyword]:
                    if re.search(rf'\b{synonym}\b', resume_text, re.IGNORECASE):
                        matches += (1 * weights[category])
                        break
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
        score = calculate_score(resume_text, weights)
        ranked_resumes.append((resume_path, score))
    return ranked_resumes