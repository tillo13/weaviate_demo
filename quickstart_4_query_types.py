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

###SET GLOBAL VARIABLES

# Set search via method parameter
SEARCH_VIA_METHOD = "near_text"
#SEARCH_VIA_METHOD = "near_object" 
#SEARCH_VIA_METHOD = "bm25" 
#SEARCH_VIA_METHOD = "ask" 
#SEARCH_VIA_METHOD = "hybrid" 

# Set an overall question
GLOBAL_QUESTION = "What animal is heavy?"

# Set a global response from Weaviate limit for each question.
GLOBAL_RETURN_LIMIT = 5

# Initialize Weaviate client
client = weaviate.Client(
    url = WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY),
    additional_headers = {"X-OpenAI-Api-Key": OPENAI_API_KEY}
)

if SEARCH_VIA_METHOD == "near_text":
    response = (
        client.query
        .get("Question", ["question", "answer", "category", "_additional {certainty}"])
        .with_near_text({"concepts": [GLOBAL_QUESTION]})
        .with_limit(GLOBAL_RETURN_LIMIT)
        .do()
    )
elif SEARCH_VIA_METHOD == "near_object":
    response = (
        client.query
        .get("Question", ["question", "answer", "category"])
        .with_near_object({
            "id": "21281c63-39c9-4834-a085-ad9bacf312a8",  # replace with your data object id
            "distance": 0.5  # the max allowed distance to the provided search input
            # or
            # "certainty": 0.7  # normalized distance between the result item and the search vector
        })
        .with_limit(GLOBAL_RETURN_LIMIT)
        .with_additional(["distance"])  # or "certainty" 
        .do()
    )
elif SEARCH_VIA_METHOD == "bm25":
    response = (
        client.query
        .get("Question", ["question", "answer", "category", "_additional {score}"])
        .with_bm25(GLOBAL_QUESTION)
        .with_limit(GLOBAL_RETURN_LIMIT)
        .do()
    )
elif SEARCH_VIA_METHOD == "ask":
    response = (
        client.query
        .get("Question", ["question", "answer", "category", "_additional {answer {property startPosition endPosition result}}"])
        .with_ask({"question": GLOBAL_QUESTION})
        .with_limit(GLOBAL_RETURN_LIMIT)
        .do()
    )
elif SEARCH_VIA_METHOD == "hybrid":
    hybrid_vector = [0.1, 0.2, 0.3, 0.4, 0.5]  # replace with your own vector if you want to use this option
    hybrid_properties = ["question"]  # replace with your desired properties
    alpha = 0.5
    additional_values = ["score"]

    response = (
        client.query
        .get("Question", ["question", "answer", "category"])
        .with_additional(additional_values)
        .with_hybrid(query=GLOBAL_QUESTION, alpha=alpha, vector=hybrid_vector, properties=hybrid_properties)
        .with_limit(GLOBAL_RETURN_LIMIT)
        .do()
    )

print(json.dumps(response, indent=4))