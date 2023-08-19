import weaviate
import os
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the variables
WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize Weaviate client
client = weaviate.Client(
    url = WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    additional_headers = {
        "X-OpenAI-Api-Key": OPENAI_API_KEY
    }
)
response = (
    client.query
    .get("Question", ["question", "answer", "category"])
    .with_near_text({"concepts": ["sound"]})
    .with_limit(5)
    .do()
)
print(json.dumps(response, indent=4))