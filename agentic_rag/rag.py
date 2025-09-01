from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseRetriever, Document
from typing import List

# Custom retriever combining two retrievers and performing combined retrieval/truncation
class CombinedRetriever(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever], max_docs_per_source: int = 3):
        self.retrievers = retrievers
        self.max_docs_per_source = max_docs_per_source

    def get_relevant_documents(self, query: str) -> List[Document]:
        combined_docs = []
        for retriever in self.retrievers:
            docs = retriever.get_relevant_documents(query)[: self.max_docs_per_source]
            combined_docs.extend(docs)
        return combined_docs

def get_personal_chroma_retriever() -> Chroma:
    return Chroma(persist_directory="./personal_chroma")

def get_external_chroma_retriever() -> Chroma:
    return Chroma(persist_directory="./external_chroma")

def main():
    personal_retriever = get_personal_chroma_retriever().as_retriever(search_kwargs={"k": 5})
    external_retriever = get_external_chroma_retriever().as_retriever(search_kwargs={"k": 5})

    combined_retriever = CombinedRetriever([personal_retriever, external_retriever], max_docs_per_source=3)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = OpenAI(temperature=0)

    # LangChain ConversationalRetrievalChain uses retriever and memory internally
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=combined_retriever,
        memory=memory,
        return_source_documents=False,
    )

    termination_signal = False
    while not termination_signal:
        user_query = input("Enter your query (or 'exit' to quit): ").strip()
        if user_query.lower() == "exit":
            termination_signal = True
            continue

        result = rag_chain.run(user_query)

        # write ans to frontend using axios
        print(result)

if __name__ == "__main__":
    main()
