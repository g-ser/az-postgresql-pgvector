from psycopg2 import connect
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.pgvector import PGVector
import os

pghost = os.getenv("PGHOST")
pguser = os.getenv("PGUSER")
pgpassword = os.getenv("PGPASSWORD")
pgdatabase = os.getenv("PGDATABASE")
pgport = os.getenv("PGPORT")
openai_api_key = os.getenv("OPENAI_API_KEY")
az_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = "embeddings"
collection_name = "state_of_the_union_vectors"


# Read the text file 
loader = TextLoader('./assets/data/state_of_the_union.txt', encoding='utf-8')
documents = loader.load()

# Split the text file into chunks

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=80)
texts = text_splitter.split_documents(documents)

# Get each one of the chunks created above and create a vector (or an embedding) from the text that is contained in each chunk

embeddings = AzureOpenAIEmbeddings(azure_endpoint=az_openai_endpoint, api_key=openai_api_key, deployment=deployment_name)
doc_vectors = embeddings.embed_documents([t.page_content for t in texts[:5]])

# Create a connection string to the Azure PostgreSQL database
conn_string = f"postgresql+psycopg2://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}"

# Create a PGVector db object
# From the PGVector class call the from_documents static method to create the db object
db = PGVector.from_documents(embedding=embeddings, documents=texts, collection_name=collection_name, connection_string=conn_string)

query = "What did the president say about Russia?"

similar = db.similarity_search_with_score(query, k=2)

for doc in similar:
    print(doc)