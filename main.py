import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient
from llm import get_JD_tags, assess_candidate_fit
from pydantic import BaseModel
from typing import List

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions
tags_collection = db["tags"]  # Collection for Tags

nlp = spacy.load("en_core_web_sm")

def add_JD_tags_and_reqs(JD_path):
    JD_text = parse_resume(JD_path)
    tags_and_reqs = get_JD_tags(JD_text)


    print(tags_and_reqs)
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

        # Assess candidate fit and generate tags using LLM
        job_requirements = list(jd_collection.find_one({"category": "Job Requirements"})['data'])  # Define or retrieve the job requirements
        llm_response = assess_candidate_fit(job_requirements, resume_text)

        # Extract tags from both LLM and resume using NLP
        llm_tags = set(llm_response['education'] + llm_response['work_experience'] +
                       llm_response['skills'] + llm_response['certifications'] +
                       llm_response['projects'] + llm_response['additional_info'])

        # Use Spacy to extract additional NLP tags if necessary
        nlp_tags = set([token.text.lower() for token in nlp(resume_text) if not token.is_space and not token.is_punct])  # Populate this set with additional NLP tags if required

        # Combine LLM tags and NLP tags uniquely
        combined_tags = llm_tags.union(nlp_tags)

        # Calculate score based on combined tags if necessary (customize scoring logic if needed)
        score = calculate_score(" ".join(combined_tags), weights)  # Use combined_tags if needed for scoring logic

        ranked_resumes.append((resume_path, llm_response['is_fit'], score, llm_response['reasoning']))
    return ranked_resumes

# print(list(jd_collection.find_one({"category": "Education"})['data']))

# jd_collection.delete_many({})
