import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions
tags_collection = db["tags"]  # Collection for Tags

nlp = spacy.load("en_core_web_sm")

# Function to rank resumes (existing)
# Function to rank resumes (existing)
def keyword_matching(resume_text, category, keywords, weights):
    matches = 0
    for keyword in keywords:
        if re.search(rf'\b{keyword}\b', resume_text, re.IGNORECASE):
            matches += (1 * weights[category])
        else:
            # Retrieve synonyms from the tags collection for the current category
            synonyms = tags_collection.find_one({"category": category}, {"_id": 0, keyword: 1})
            if synonyms and keyword in synonyms:
                for synonym in synonyms[keyword]:
                    if re.search(rf'\b{synonym}\b', resume_text, re.IGNORECASE):
                        matches += (1 * weights[category])
                        break
    return matches

def calculate_score(resume_text, weights):
    total_score = 0
    resume_text = " ".join([token.text.lower() for token in nlp(resume_text) if not token.is_space and not token.is_punct])
    
    job_descriptions = list(jd_collection.find({}, {"_id": 0}))
    # Iterate through each category in job description
    for category, keywords in job_descriptions[0].items():
        if category == "_id" or category == "title":
            continue  # Skip MongoDB metadata fields
        keyword_matches = keyword_matching(resume_text, category, keywords, weights)
        max_matches = len(keywords)
        
        if max_matches > 0:
            score = (keyword_matches / max_matches) * 100
            total_score += score
    return total_score

def rank_resumes(resume_paths, weights):
    ranked_resumes = []
    for resume_path in resume_paths:
        resume_text = parse_resume(resume_path)
        score = calculate_score(resume_text, weights)
        ranked_resumes.append((resume_path, score))
    return ranked_resumes