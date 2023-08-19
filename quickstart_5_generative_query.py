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

# Set up our global question.
GLOBAL_QUESTION = "What animal is heavy?"

# Set response from Weaviate limit for each question.
GLOBAL_RETURN_LIMIT = 1

# Initialize Weaviate client
client = weaviate.Client(
    url = WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    additional_headers = {"X-OpenAI-Api-Key": OPENAI_API_KEY}
)

# The prompt which will be used with the generative AI model.
generate_prompt = "Describe what makes the {answer} a heavy animal."

response = (
  client.query
  .get('Question', ['question', 'answer', 'category'])
  .with_generate(single_prompt=generate_prompt)
  .with_near_text({
    'concepts': ['heavy animal']
  })
  .with_limit(GLOBAL_RETURN_LIMIT)
).do()

print(json.dumps(response, indent=2))