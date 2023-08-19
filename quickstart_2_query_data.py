import os
import weaviate
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')

VERBOSE_MODE = False # Set it to True if you want to see vector data

client = weaviate.Client(
    url=WEAVIATE_URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY)
)

batch_size = 100
class_name = "Question"
class_properties = ["question", "answer", "category"]
cursor = None

def get_batch_with_cursor(client, class_name, class_properties, batch_size, cursor=None):
    query = (
        client.query.get(class_name, class_properties)
        .with_additional(["id", "creationTimeUnix"] if not VERBOSE_MODE else ["id", "creationTimeUnix", "vector"])
        .with_limit(batch_size)
    )

    if cursor is not None:
        return query.with_after(cursor).do()
    else:
        return query.do()


table_headers = ["Line", "ID", "Creation Time", "Category", "Question"]

if VERBOSE_MODE:
    table_headers.append("Vector")

table_headers.append("Answer")

table_data = []

while True:
    results = get_batch_with_cursor(client, class_name, class_properties, batch_size, cursor)
    objects_list = results["data"]["Get"][class_name]

    if not objects_list:
        break

    for obj in objects_list:
        # truncate question to 10 characters 
        truncated_question = obj["question"][:30] + '...' if len(obj["question"]) > 10 else obj["question"]
        # rearrange data
        row_data = [obj["_additional"]["id"], obj["_additional"]["creationTimeUnix"], obj["category"], truncated_question]
        
        if VERBOSE_MODE:
            row_data.append(obj["_additional"]["vector"])
        
        row_data.append(obj["answer"])
        table_data.append(row_data)
    
    cursor = objects_list[-1]["_additional"]["id"]

# Sort table_data by question and add line count
table_data = sorted(table_data, key=lambda row: row[4])

# Add line count before ID, shift rest of the columns to right
table_data = [[f"{i+1}"] + row for i, row in enumerate(table_data)]

if VERBOSE_MODE:
    for i, row in enumerate(table_data):
        print("=====")
        print(f"Line: {i+1}")
        print(f"ID: {row[1]}")
        print(f"Creation Time: {row[2]}")
        print(f"Category: {row[3]}")
        print(f"Question: {row[4]}")
        print(f"Answer: {row[6]}")
        if VERBOSE_MODE:
            print(f"Vector Embeddings: {row[5]}")
        print("=====")
else:
    print(tabulate(table_data, headers=table_headers, tablefmt='pretty'))