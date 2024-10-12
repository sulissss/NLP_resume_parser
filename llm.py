from openai import OpenAI
from typing import List
from pydantic import BaseModel
import instructor
import json

class JobDescription(BaseModel):
    tags: List[str]
    requirements: List[str]

# class LLMScreener(BaseModel):
#     is_fit: bool
#     reasoning: str
#     tags: List[str]

class LLMScreener(BaseModel):
    is_fit: bool
    reasoning: str
    education: List[str]
    work_experience: List[str]
    skills: List[str]
    certifications: List[str]
    projects: List[str]
    additional_info: List[str]


client = instructor.from_openai(OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama',
),
    mode=instructor.Mode.JSON
)

def get_JD_tags_and_reqs(JD_text):
    return json.loads(
                client.chat.completions.create(
                    model="llama3",
                    max_retries=3,
                    messages=[{"role": "system", "content": f"You are part of an NLP resume screener. You need to generate tags, i.e. important keywords from the following Job Description that would be matched with resumes to evaluate a score. Furthermore, you also need to list the requirements for the job (requirements which are strict). Job description: {JD_text}"}],
                    response_model=JobDescription
                ).model_dump_json(indent=2)
            ) 

# def is_fit_screener(job_reqs, resume_text):
#     return json.loads(
#         client.chat.completions.create(
#                 model="llama3",
#                 max_retries=3,
#                 messages=[{"role": "system", "content": f"You are part of an NLP resume screener. You have been given the job requirements and a resume, on the basis of which you have to output if the candidate is fit for the job or not. Also provide reasoning as to why you considered the candidate to be fit or not fit for the job. If the candidate is a fit, extract relevant tags, i.e. important keywords from the resume that would aid in keyword matching with the job description. Job requirements: {job_reqs}\n The resume: {resume_text}"}],
#                 response_model=LLMScreener
#             ).model_dump_json(indent=2)
#     )

def assess_candidate_fit(job_requirements, resume_text):
    return json.loads(
        client.chat.completions.create(
            model="llama3",
            max_retries=3,
            messages=[
                {"role": "system", "content": f"""
                You are part of a resume screener. Based on the job requirements and the resume provided, determine if the candidate is fit for the job and explain your reasoning. 
                Additionally, generate tags, i.e. important keywords from the resume, which includes the candidate's Education, Work Experience, Skills, Certifications, Projects, and other Additional Info. 
                Replace these keywords with their popular synonyms for better keyword matching. Leave any field blank if the data is unavailable.
                Job requirements: {job_requirements}
                Resume: {resume_text}
                """}
            ],
            response_model=LLMScreener
        ).model_dump_json(indent=2)
    )


if __name__ == "__main__":
    pass