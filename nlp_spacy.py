import json
import re
import os
import spacy
from utils import parse_resume

nlp = spacy.load("en_core_web_sm")

DOCS_PATH = "/Applications/Documents/Tags, Ranking and Sample CVs/Sample CVs"
file_name = "Alfowzan.pdf"


# Function to rank resumes (existing)
def keyword_matching(resume_text, category, keywords, weights, tags):
    matches = 0
    for keyword in keywords:
        if re.search(rf'\b{keyword}\b', resume_text, re.IGNORECASE):
            matches += (1 * weights[category])
        else:
            if keyword in tags[category]:
                for synonym in tags[category][keyword]:
                    if re.search(rf'\b{synonym}\b', resume_text, re.IGNORECASE):
                        matches += (1 * weights[category])
                        break
    return matches

def calculate_score(resume_text, job_description, weights, tags):
    total_score = 0
    resume_text = " ".join([token.text.lower() for token in nlp(resume_text) if not token.is_space and not token.is_punct])
    
    for category, keywords in job_description.items():
        keyword_matches = keyword_matching(resume_text, category, keywords, weights, tags)
        max_matches = len(keywords)
        
        if max_matches > 0:
            score = (keyword_matches / max_matches) * 100
            total_score += score
    return total_score

def rank_resumes(resume_paths, job_description, weights, tags):
    ranked_resumes = []
    for resume_path in resume_paths:
        resume_text = parse_resume(resume_path)
        score = calculate_score(resume_text, job_description, weights, tags)
        final_score = score
        ranked_resumes.append((resume_path, final_score))
    return ranked_resumes

