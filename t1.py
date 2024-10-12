import json
import re
import os
import spacy
from utils import parse_resume
from pymongo import MongoClient
from llm import get_JD_tags_and_reqs, assess_candidate_fit
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
    tags_and_reqs = get_JD_tags_and_reqs(JD_text)


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

def rank_resume(resume_path, weights):
    resume_text = parse_resume(resume_path)
    job_requirements = list(jd_collection.find_one({"category": "Job Requirements"})['data'])
    resume_tags = assess_candidate_fit(job_requirements, resume_text)

    # embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    if resume_tags['is_fit']:
        for category in ['education', 'work_experience', 'skills', 'certifications', 'projects', 'additional_info']:
            for tags in resume_tags[category]:
                ## apply keyword matching logic between each tag in tags and all tags in the JD collection
                ## the keyword matching logic must increment matches, if cosine similarity score is above a certain threshold
                pass


