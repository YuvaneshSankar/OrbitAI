from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

def debug_pinecone_content():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
    vectorstore = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX,
        embedding=embeddings,
    )
    
    # Get some documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents("news")
    
    print("=== DEBUGGING PINECONE CONTENT ===\n")
    
    for i, doc in enumerate(docs):
        print(f"Document {i+1}:")
        print(f"Page Content: {doc.page_content}")
        print(f"Metadata Keys: {list(doc.metadata.keys())}")
        print("Sample Metadata:")
        for key, value in list(doc.metadata.items())[:10]:  # Show first 10 metadata items
            print(f"  {key}: {str(value)[:100]}...")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    debug_pinecone_content()
