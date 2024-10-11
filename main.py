import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient
from llm import get_JD_tags_and_reqs, is_fit_screener

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
    # Normalize the resume text
    resume_text = " ".join([token.text.lower() for token in nlp(resume_text) if not token.is_space and not token.is_punct])
    
    # Retrieve all job descriptions
    job_descriptions = list(jd_collection.find({}, {"_id": 0}))
    
    # Iterate through each job description document
    for category_doc in job_descriptions:
        category = category_doc['category']  # Access the category
        keywords = category_doc['data']  # Access the keywords in the data field
        
        # Perform keyword matching for the current category
        keyword_matches = keyword_matching(resume_text, category, keywords, weights)
        max_matches = len(keywords)
        
        # Calculate score if there are keywords to match against
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

def add_JD_tags_and_reqs(JD_path):
    JD_text = parse_resume(JD_path)
    tags_and_reqs = get_JD_tags_and_reqs(JD_text)
    # add tags_and_reqs['tags'] to the tags collection
    # add tags_and_reqs['requirements'] as a new document in the JD collection
