from openai import OpenAI
from typing import List
from pydantic import BaseModel
import instructor
import json

class JobDescription(BaseModel):
    education: List[str]
    work_experience: List[str]
    skills: List[str]
    projects: List[str]
    certifications: List[str]
    additional_info: List[str]
    job_requirements: List[str]

# class LLMScreener(BaseModel):
#     is_fit: bool
#     reasoning: str
#     tags: List[str]

# class LLMScreener(BaseModel):
#     is_fit: bool
#     reasoning: str
#     education: List[str]
#     work_experience: List[str]
#     skills: List[str]
#     certifications: List[str]
#     projects: List[str]
#     additional_info: List[str]
    
class MatchesOutput(BaseModel):
    education: int
    work_experience: int
    skills: int
    projects: int
    certifications: int
    additional_info: int
    is_fit: bool
    reasoning: str


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
        temperature=0.0,
        max_retries=3,
        messages=[{
            "role": "system", 
            "content": f"""You are a precise resume evaluator. Based on the following job description tags and resume text, perform the following tasks:

**Task 1**: Count the tags from the job description that are present in the resume text for each category. Consider synonyms, variations, and similar terms to ensure accurate matching.

For example, if the job description contains:
- 'education': ['Bachelor's in CS', 'Master's in Engineering']
- 'work_experience': ['two years']
- 'skills': ['ASP.NET framework', 'SQL Server']
- 'projects': ['web application development']
- 'certifications': ['AWS Certified']
- 'additional_info': ['positive attitude']

And the resume text is:
'I have completed my Bachelor's degree in Computer Science. I have over two years of experience as a software developer, specializing in ASP.NET framework and SQL Server. I am AWS Certified and have worked on web application development. I am known for my troubleshooting skills and have good communication skills. I am a self-starter who requires minimal supervision and maintain a positive attitude.'

Your output should look like this:
{{'education': 1, 'work_experience': 1, 'skills': 2, 'projects': 1, 'certifications': 1, 'additional_info': 1}} 

**Task 2**: Evaluate if the candidate is fit for the job, based the job requirements, and provide a reasoning as to why.

Job Description Tags:
{job_requirements}

Resume Text:
{resume_text}""".strip()
        }],
        response_model=MatchesOutput
    ).model_dump_json(indent=4)
)


if __name__ == "__main__":
    pass