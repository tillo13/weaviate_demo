import weaviate
import os
import json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# setup the variables
WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize Weaviate client
client = weaviate.Client(
    url = WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    additional_headers = {"X-OpenAI-Api-Key": OPENAI_API_KEY}
)

# Set the ID of the object you want to update and the new Answer
uuid = '21281c63-39c9-4834-a085-ad9bacf312a8'
new_answer = 'Dog'

# Update the object's Answer
client.data_object.update(
    uuid=uuid,
    class_name='Question',
    data_object={'Answer': new_answer,
    },
)

print(f"Updated ID {uuid}'s answer to {new_answer}")