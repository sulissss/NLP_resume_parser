import requests

# Base URL of the API
BASE_URL = 'http://127.0.0.1:5000'  # Change this to your actual API URL

# Define the API endpoints and their expected responses
api_tests = {
    'upload_resumes': {
        'url': f'{BASE_URL}/resume/upload_resumes',
        'method': 'POST',
        'data': {'resumes': ('dummy_resume.pdf', open('dummy_resume.pdf', 'rb'))},  # Change to a valid resume file
        'expected': 200
    },
    'delete_resumes': {
        'url': f'{BASE_URL}/resume/delete_resumes',
        'method': 'DELETE',
        'data': {'resumes': ['dummy_resume.pdf']},
        'expected': 200
    },
    'delete_all_resumes': {
        'url': f'{BASE_URL}/resume/delete_all_resumes',
        'method': 'DELETE',
        'expected': 200
    },
    'get_resume_scores': {
        'url': f'{BASE_URL}/resume/get_resume_scores',
        'method': 'GET',
        'expected': 200
    },
    'create_JDs': {
        'url': f'{BASE_URL}/JD/create_JDs',
        'method': 'POST',
        'data': {'Software Engineer': ['Python', 'Java']},
        'expected': 201
    },
    'update_JDs': {
        'url': f'{BASE_URL}/JD/update_JDs',
        'method': 'PUT',
        'data': {'job_title': 'Software Engineer', 'new_key': 'new_value'},
        'expected': 200
    },
    'delete_JD': {
        'url': f'{BASE_URL}/JD/delete_JD',
        'method': 'DELETE',
        'data': {'job_title': 'Software Engineer'},
        'expected': 200
    },
    'get_all_JDs': {
        'url': f'{BASE_URL}/JD/get_all_JDs',
        'method': 'GET',
        'expected': 200
    },
    'create_tags': {
        'url': f'{BASE_URL}/tag/create_tags',
        'method': 'POST',
        'data': {'skills': ['Python', 'JavaScript']},
        'expected': 201
    },
    'delete_tag': {
        'url': f'{BASE_URL}/tag/delete_tag',
        'method': 'DELETE',
        'data': {'tag_name': 'Python'},
        'expected': 200
    },
    'get_all_tags': {
        'url': f'{BASE_URL}/tag/get_all_tags',
        'method': 'GET',
        'expected': 200
    },
    'set_weights': {
        'url': f'{BASE_URL}/weights/set_weights',
        'method': 'POST',
        'data': {'category1': 1, 'category2': 2},
        'expected': 200
    },
    'get_weights': {
        'url': f'{BASE_URL}/weights/get_weights',
        'method': 'GET',
        'expected': 200
    },
    'create_subJD': {
        'url': f'{BASE_URL}/subJD/create_subJD',
        'method': 'POST',
        'data': {'job_title': 'Software Engineer', 'subJD_details': 'Details about the subJD'},
        'expected': 201
    },
    'delete_subJD': {
        'url': f'{BASE_URL}/subJD/delete_subJD',
        'method': 'DELETE',
        'data': {'job_title': 'Software Engineer'},
        'expected': 200
    },
    'get_all_subJDs': {
        'url': f'{BASE_URL}/subJD/get_all_subJDs',
        'method': 'GET',
        'expected': 200
    },
    'create_subtag': {
        'url': f'{BASE_URL}/subtag/create_subtag',
        'method': 'POST',
        'data': {'tag_name': 'Python', 'subtag_details': 'Details about the subtag'},
        'expected': 201
    },
    'delete_subtag': {
        'url': f'{BASE_URL}/subtag/delete_subtag',
        'method': 'DELETE',
        'data': {'tag_name': 'Python'},
        'expected': 200
    },
    'get_all_subtags': {
        'url': f'{BASE_URL}/subtag/get_all_subtags',
        'method': 'GET',
        'expected': 200
    }
}

# Function to test the APIs
def test_api(api_name, url, method, data=None, expected=None):
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data, files=data if isinstance(data, dict) and 'resumes' in data else None)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, json=data)
        
        # Check if the response status code matches the expected value
        success = (response.status_code == expected)
        print(f"{api_name}: {'Success' if success else 'Failed'} (Status Code: {response.status_code})")
        return success
    except Exception as e:
        print(f"{api_name}: Error occurred - {e}")
        return False

# Iterate through the API tests and execute them
results = {api_name: test_api(api_name, **test_info) for api_name, test_info in api_tests.items()}

# Output the results
print("\nAPI Test Results:")
for api_name, result in results.items():
    print(f"{api_name}: {'Passed' if result else 'Failed'}")