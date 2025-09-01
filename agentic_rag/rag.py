from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseRetriever, Document
from typing import List
import heapq

class CombinedRetriever(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever], llm: OpenAI, max_docs_per_source: int = 3, top_k_after_rerank: int = 3):
        self.retrievers = retrievers
        self.llm = llm
        self.max_docs_per_source = max_docs_per_source
        self.top_k_after_rerank = top_k_after_rerank

    def _score_doc(self, query: str, doc: Document) -> float:
        prompt = (
            f"Rate the relevance of the following document to the query on a scale of 1 to 5 (5=most relevant):\n\n"
            f"Query: {query}\n\nDocument:\n{doc.page_content}\n\nScore:"
        )
        score_str = self.llm(prompt).strip()
        try:
            score = float(score_str)
        except ValueError:
            score = 0.0  # fallback if parsing fails
        return score

    def get_relevant_documents(self, query: str) -> List[Document]:
        combined_docs = []
        for retriever in self.retrievers:
            docs = retriever.get_relevant_documents(query)[: self.max_docs_per_source]
            combined_docs.extend(docs)

        # Rerank using LLM scores (descending order)
        scored_docs = []
        for doc in combined_docs:
            score = self._score_doc(query, doc)
            heapq.heappush(scored_docs, (-score, doc))

        top_docs = []
        for _ in range(min(self.top_k_after_rerank, len(scored_docs))):
            top_docs.append(heapq.heappop(scored_docs)[1])

        return top_docs


def get_personal_chroma_retriever() -> Chroma:
    return Chroma(persist_directory="./personal_chroma")


def get_external_chroma_retriever() -> Chroma:
    return Chroma(persist_directory="./external_chroma")


def main():
    llm = OpenAI(temperature=0)

    personal_retriever = get_personal_chroma_retriever().as_retriever(search_kwargs={"k": 5})
    external_retriever = get_external_chroma_retriever().as_retriever(search_kwargs={"k": 5})

    combined_retriever = CombinedRetriever(
        [personal_retriever, external_retriever], llm=llm, max_docs_per_source=5, top_k_after_rerank=3
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

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
        #write to frontend
        print(result)


if __name__ == "__main__":
    main()
