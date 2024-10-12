# import os
# from pinecone import Pinecone, ServerlessSpec

# pc = Pinecone(
#     api_key='fcee3d28-5334-44ea-96ec-fb4a3ba5438d'
# )

# # Create an index
# index_name = "resume-tags-index"
# if index_name not in pc.list_indexes():
#     pc.create_index(index_name, dimension=768) 

from sentence_transformers import SentenceTransformer

class EmbeddingFunctionWrapper:
    def __init__(self):
        ## Use "dunzhang/stella_en_400M_v5" as the alternative
        # self.model = SentenceTransformer("Alibaba-NLP/gte-Qwen2-1.5B-instruct", trust_remote_code=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_documents(self, texts):
        # The model expects a list of texts
        return self.model.encode(texts, convert_to_tensor=False).tolist()
    
    def embed_query(self, query):
        # The model expects a single query text
        return self.model.encode([query], convert_to_tensor=False).tolist()[0]


def get_embedding_function():
    return EmbeddingFunctionWrapper()


from langchain_chroma import Chroma

# Initialize ChromaDB vector store
chroma_db = Chroma(persist_directory='chromadb',
    embedding_function=get_embedding_function()
    )

# Sample job description tags
job_description_tags = [
    {
        "category": "education",
        "data": ["bachelor's degree in computer science or computer engineering or equivalent"]
    },
    {
        "category": "work_experience",
        "data": ["minimum two years"]
    }
]

# Step 1: Store job description tags into the ChromaDB
for tag in job_description_tags:
    category = tag["category"]
    for data in tag["data"]:
        # Add the tag to the vector store
        chroma_db.add_texts([data], metadatas=[{"category": category}])


# Sample resume tags
resume_tags = {
    'education': ['bachelors_degree', 'computer science'],
    'work_experience': ['minimum_two_years'],
    'skills': ['troubleshooting', 'written_communication', 'communication'],
    'projects': [],
    'certifications': ['relevant_certifications'],
    'additional_info': ['self_starter', 'positive_attitude'],
    'job_requirements': ['minimum_two_years']
}

def search_resume_tags(chroma_db, resume_tags, threshold=0.5):
    results_count = {}

    # Iterate over each category in the resume tags
    for category, tags in resume_tags.items():
        results_count[category] = 0  # Initialize the count for this category

        for tag in tags:
            # Perform similarity search
            search_results = chroma_db.similarity_search(tag)

            # Check results against the threshold
            for result in search_results:
                # Check if result contains a 'score' or 'similarity' attribute
                similarity = result.metadata.get('similarity', None)  # Adjust based on actual attributes
                print(result)
                if similarity is not None and similarity > threshold:
                    results_count[category] += 1

    return results_count

# # Call the function to perform the search
# threshold = 0.7  # Set your desired threshold
# matches = search_resume_tags(chroma_db, resume_tags, threshold)

# # Print results
# print(f"Matches above threshold: {matches}")

print(chroma_db.similarity_search("minimum 2 years"))