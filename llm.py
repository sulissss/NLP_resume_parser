from openai import OpenAI
from typing import List
from pydantic import BaseModel
import instructor
import json

llm_model = "llama3"

class JobDescription(BaseModel):
    education: List[str]
    work_experience: List[str]
    skills: List[str]
    projects: List[str]
    certifications: List[str]
    additional_info: List[str]
    job_requirements: List[str]

class LLMScreener(BaseModel):
    is_fit: bool
    reasoning: str

class ResumeOrNot(BaseModel):
    is_resume: bool

client = instructor.from_openai(OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama',
),
    mode=instructor.Mode.JSON
)

def get_JD_tags(JD_text):
    return json.loads(
            client.chat.completions.create(
                model="llama3",
                max_retries=3,
                messages=[{
                    "role": "system", 
                    "content": (
                        f"You are a part of an NLP resume screener. Divide your task into two."
                        f" First, extract keywords from the following Job Description and categorize them as"
                        f" Education, Work Experience, Skills, Certifications, Work Projects, and Additional Info."
                        f" STRICTLY ensure that ALL keywords are a maximum of TWO words. Avoid phrases, avoid stopwords, keep it concise."
                        f" For example, instead of 'excellent troubleshooting skills', use 'troubleshooting'."
                        f" Also ensure to separate compound keywords ONLY WHERE NECESSARY, e.g., 'html5/css3/javascript' becomes 'html5', 'css3', 'javascript'."
                        f" Second, list the strict requirements for the job, including minimum experience."
                        f" Leave any field blank if no data is available."
                        f" Job description: {JD_text}"
                    )
                }],
                response_model=JobDescription
            ).model_dump_json(indent=4)
        )

def assess_candidate(job_reqs, resume_text):
    return json.loads(
        client.chat.completions.create(
                model=llm_model,
                max_retries=3,
                messages=[{"role": "system", "content": 
                           f"You are part of a resume screener. Based on the job requirements and the resume provided, determine if the candidate is fit for the job and explain your reasoning.\n Job requirements: {job_reqs}, Resume: {resume_text}"}],
                response_model=LLMScreener
            ).model_dump_json(indent=2)
        )

def resume_or_not(data):
    return json.loads(
        client.chat.completions.create(
                model=llm_model,
                max_retries=3,
                messages=[{"role": "system", "content": 
                           f"Evaluate whether the following text is a candidate's resume, or a job description: {data}"}],
                response_model=ResumeOrNot
            ).model_dump_json(indent=2)
        )

if __name__ == "__main__":
    pass