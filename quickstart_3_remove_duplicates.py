import weaviate
import os
from dotenv import load_dotenv


def fetch_questions(client):
    class_name = 'Question'
    class_properties = ['question']
    limit = 100
    cursor = None
    all_questions = []

    while True:
        results = get_batch_with_cursor(client, class_name, class_properties, limit, cursor)
        if not results["data"]["Get"][class_name]:
            break
            
        all_questions.extend(results["data"]["Get"][class_name])
        
        cursor = results["data"]["Get"][class_name][-1]["_additional"]["id"]

    return all_questions

def get_batch_with_cursor(client, class_name, class_properties, limit, cursor=None):
    query = (
        client.query.get(class_name, class_properties)
        .with_additional(["id"])
        .with_limit(limit)
    )

    if cursor is not None:
        return query.with_after(cursor).do()
    else:
        return query.do()

def remove_duplicates(client, all_questions):
    question_dict = {}
    
    for question in all_questions:
        question_text = question["question"]
        if question_text in question_dict:
            question_dict[question_text].append(question["_additional"]["id"])
        else:
            question_dict[question_text] = [question["_additional"]["id"]]

    # Iterating through the questions to delete duplicates
    for question, ids in question_dict.items():
        if len(ids) > 1:
            print(f"Found duplicates for the question '{question}'. Deleting duplicates.")
            # Keep the first one (earliest by insertion), delete the rest
            for id in ids[1:]:
                print(f"Deleting question with id: {id}")
                client.data_object.delete(class_name='Question', uuid=id)
            print(f"Keeping question with id: {ids[0]}\n")
        else:
            print(f"No duplicates found for the question '{question}'.\n")

def delete_duplicates():
    load_dotenv()
    
    WEAVIATE_URL = os.getenv('WEAVIATE_URL')
    WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')

    client = weaviate.Client(
        url=WEAVIATE_URL,
        auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)
    )
    
    all_questions = fetch_questions(client)
    remove_duplicates(client, all_questions)

if __name__ == "__main__":
    delete_duplicates()