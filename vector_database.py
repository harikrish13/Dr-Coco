from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


client = OpenAI(api_key= "")
existing_vector_stores = client.beta.vector_stores.list()
vector_store = None
for store in existing_vector_stores.data:
    if store.name == "MentalDisorder Database - 2":
        vector_store = store
        break
if vector_store is None:
    vector_store = client.beta.vector_stores.create(name="MentalDisorder Database - 2")

# Ready the files for upload to OpenAI
file_paths = ["C://Users//hari2//Desktop//hack duke//faq.json"]  # Add files of any format here
file_streams = [open(path, "rb") for path in file_paths]

file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)

print(file_batch.status)
print(file_batch.file_counts)
