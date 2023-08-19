# 2023aug18 from https://weaviate.io/developers/weaviate/quickstart
import os
import requests
import json
from dotenv import load_dotenv
import weaviate

# Loading values from .env file
load_dotenv()

# Accessing environment variables
WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initializing the Weaviate client with the given URL, 
# Weaviate API key, and OpenAI API key.
client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    additional_headers={
        "X-OpenAI-Api-Key": OPENAI_API_KEY
    }
)
class_name = "Question"

# Fetching the current schema from Weaviate
schema = client.schema.get()

# Checking if the class 'Question' already exists in the Weaviate schema
if class_name not in [klass['class'] for klass in schema['classes']]:
    # If 'Question' class doesn't exist, we create it
    class_obj = {
        "class": class_name,
        "vectorizer": "text2vec-openai",  
        "moduleConfig": {
            "text2vec-openai": {},
            "generative-openai": {}
        }
    }

    client.schema.create_class(class_obj)
    print(f"Class '{class_name}' created.")
else:
    # If 'Question' class already exists, notify the user
    print(f"Class '{class_name}' already exists.")

# Downloading the dataset from the GitHub repo
resp = requests.get('https://raw.githubusercontent.com/weaviate-tutorials/quickstart/main/data/jeopardy_tiny.json')
data = json.loads(resp.text)  # Parsing the dataset into JSON format

# Small function to check if an object already exists in Weaviate
def object_exists(client, obj):
    # Getting all objects of class 'Question'
    result_objs = client.query.get(class_name, ['question', 'answer', 'category']).do()
    result_objs = result_objs['data']['Get'][class_name]

    # Looping through the existing objects and comparing with the
    # given object. If a match is found, the function returns True.
    for result_obj in result_objs:
        if all(obj[prop] == result_obj[prop] for prop in obj):
            return True

    # If no match is found in the loop, the function returns False
    return False

# Starting batch import process
with client.batch() as batch:  
    # Looping through each question/answer object in the downloaded dataset
    for i, d in enumerate(data):  
        # Mapping the question/answer object to the Weaviate data model
        properties = {"answer": d["Answer"], "question": d["Question"], "category": d["Category"]}

        # Before adding the object, we check if it already exists in Weaviate
        if not object_exists(client, properties):
            # If it does not exist, we add the object to Weaviate
            print(f"Importing question: '{properties['question']}'")
            batch.add_data_object(data_object=properties, class_name="Question")
        else:
            # If it already exists, we notify the user and skip this object
            print(f"Skipping question {i+1} as it is already in Weaviate: \nCategory: {properties['category']}\nQuestion: {properties['question']}\nAnswer: {properties['answer']}\n\n")