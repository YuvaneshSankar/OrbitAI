from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from typing import List

#dummy instances of chroma db 
def get_personal_chroma_retriever() -> Chroma:
    return Chroma(persist_directory="./personal_chroma")  

def get_external_chroma_retriever() -> Chroma:
    # Placeholder for external knowledge vector DB
    return Chroma(persist_directory="./external_chroma") 

class AgenticRAGWithChroma:
    def __init__(self, personal_db: Chroma, external_db: Chroma, llm_model: OpenAI):
        self.personal_retriever = personal_db.as_retriever(search_kwargs={"k": 5})
        self.external_retriever = external_db.as_retriever(search_kwargs={"k": 5})
        self.llm = llm_model
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def dynamic_retrieval(self, query: str, max_docs_per_source=3) -> List[Document]:
        # Retrieve documents from both vector DBs
        personal_docs = self.personal_retriever.get_relevant_documents(query)[:max_docs_per_source]
        external_docs = self.external_retriever.get_relevant_documents(query)[:max_docs_per_source]
        all_docs = personal_docs + external_docs
        return all_docs[:max_docs_per_source]  # limit total number of documents passed to LLM

    def generate_answer(self, user_query: str) -> str:
        chat_history = self.memory.load_memory_variables({}).get("chat_history", [])
        context_text = ""
        for msg in chat_history:
            role = msg.type.capitalize()
            content = msg.content
            context_text += f"{role}: {content}\n"

        docs = self.dynamic_retrieval(f"{context_text} {user_query}")

        prompt = (
            "You are a helpful assistant. Use the following documents to answer the question.\n\n"
            f"User Question:\n{user_query}\n\n"
            "Relevant Documents:\n"
            + "\n".join([doc.page_content for doc in docs])
            + "\n\nAnswer:"
        )
        answer = self.llm(prompt)

        # Update chat history memory
        self.memory.chat_memory.add_user_message(user_query)
        self.memory.chat_memory.add_ai_message(answer)

        return answer

def main():
    personal_chroma = get_personal_chroma_retriever()
    external_chroma = get_external_chroma_retriever()
    llm = OpenAI(temperature=0)

    rag_system = AgenticRAGWithChroma(personal_chroma, external_chroma, llm)

    # Simulated event loop for receiving repeated queries from the frontend
    termination_signal = False
    while not termination_signal:
        user_query = input("Enter your query (or 'exit' to quit): ").strip()
        if user_query.lower() == "exit":
            termination_signal = True
            continue

        # Process user query: dynamic retrieval + LLM generation + memory update
        answer = rag_system.generate_answer(user_query)

        #write answer back to frontend
        print(answer)

if __name__ == "__main__":
    main()
