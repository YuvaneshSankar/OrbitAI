from dotenv import load_dotenv
import os
from typing import List, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseRetriever, Document

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

class SimpleRetriever(BaseRetriever, BaseModel):
    retriever: BaseRetriever = Field(...)
    llm: Any = Field(...)

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str) -> List[Document]:
        # Get more documents since they're fragmented
        docs = self.retriever.get_relevant_documents(query, k=100)
        
        # Group and combine related fragments
        combined_content = []
        seen_content = set()
        
        for doc in docs:
            content = doc.page_content.strip()
            if (len(content) > 10 and 
                content not in seen_content and
                not content.startswith('"')):
                combined_content.append(content)
                seen_content.add(content)
        
        # Create a single comprehensive document
        if combined_content:
            full_content = " | ".join(combined_content[:20])  # Take top 20 fragments
            combined_doc = Document(
                page_content=full_content,
                metadata={"source": "combined", "type": "aggregated"}
            )
            print(f"Combined content preview: {full_content[:500]}...")
            return [combined_doc]
        
        return docs[:5]  # Fallback to original docs

def get_retriever():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)
    base_retriever = PineconeVectorStore.from_existing_index(
        index_name=PINECONE_INDEX,
        embedding=embeddings,
    ).as_retriever(search_kwargs={"k": 250})
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=OPENAI_API_KEY)
    return SimpleRetriever(retriever=base_retriever, llm=llm)

def main():
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=OPENAI_API_KEY)
    retriever = get_retriever()
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True,
        output_key="answer"
    )
    
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
    )

    while True:
        query = input("Enter your query (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break

        try:
            result = rag_chain({"question": query})
            print("\nRetrieved content:")
            for i, doc in enumerate(result.get("source_documents", [])):
                print(f"[Doc {i+1}]: {doc.page_content[:400]}...\n")
            print("Answer:", result["answer"])
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    main()
