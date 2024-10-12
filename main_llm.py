import json
import re
import os
import spacy
from utils import *
from pymongo import MongoClient
from llm import get_JD_tags, assess_candidate_fit
from pydantic import BaseModel
from typing import List

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["resume_management"]  # Database
jd_collection = db["job_descriptions"]  # Collection for Job Descriptions


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

def calculate_score(match_counts, weights):
    total_JDs = {}
    job_description = get_job_description()
    for category, tags in job_description.items():
        total_JDs[category] = len(tags)
    
    for category in weights:
        if match_counts[category] > total_JDs[category]:
            match_counts[category] = total_JDs[category]

    return sum(weights[cat] * (match_counts[cat] / total_JDs[cat]) for cat in weights if total_JDs[cat] != 0)


def rank_resumes(resume_paths, weights):
    ranked_resumes = []
    job_description = get_job_description()
    for resume_path in resume_paths:
        resume_text = parse_resume(resume_path)
        print(f"Resume path: {resume_path}")
        print(f"Resume Text: {resume_text}")
        candidate_data = assess_candidate_fit(job_description, resume_text)
        if candidate_data['is_fit']:
            score = calculate_score(candidate_data, weights)
            print("-------------")
            print(f"Score: {score}")
            ranked_resumes.append((resume_path, candidate_data['is_fit'], score))
        else:
            ranked_resumes.append((resume_path, candidate_data['is_fit'], candidate_data['reasoning']))
    return ranked_resumes

if __name__ == "__main__":
    pass