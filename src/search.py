import os
from dotenv import load_dotenv
from src.vectorstore import FaissVectorStore
from langchain_groq import ChatGroq

load_dotenv()

class RAGChatbot:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "llama-3.1-8b-instant"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        self.chat_history = []
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from data_loader import load_all_documents
            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
        groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def chat(self, query: str, top_k: int = 5) -> str:

        # Retrieve relevant docs
        results = self.vectorstore.query(query, top_k=top_k)

        texts = [
            r["metadata"].get("text", "")
            for r in results
            if r.get("metadata")
        ]

        context = "\n\n".join(texts)

        if not context:
            return "I couldn't find relevant information in the knowledge base."

        # Format previous conversation
        history = "\n".join(
            [f"User: {u}\nAssistant: {a}" for u, a in self.chat_history]
        )

        # Build chatbot prompt
        prompt = f"""

            You are a life sciences clinical trial query assistant. Your job is to interpret natural language questions about clinical trials, search structured registries and unstructured trial reports/publications, and return concise, accurate summaries or answers with references.

            Instructions:
            Understand trial design, population, intervention, comparator, outcomes, phase, status, and eligibility.
            Use evidence from the data and cite the source for each claim.
            When results or comparisons are best shown in tabular form, present a clean table.
            Keep answers precise, avoid speculation, and clearly note any assumptions or data limitations.
            Focus on helping researchers make decisions by translating complex clinical trial data into actionable insights.


            Conversation History:
            {history}

            Context:
            {context}

            User Question:
            {query}

            Assistant:
        """

        # Generate response
        response = self.llm.invoke(prompt)

        answer = response.content

        # Save memory
        self.chat_history.append((query, answer))

        return answer

# class RAGSearch:
#     def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "llama-3.1-8b-instant"):
#         self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
#         # Load or build vectorstore
#         faiss_path = os.path.join(persist_dir, "faiss.index")
#         meta_path = os.path.join(persist_dir, "metadata.pkl")
#         if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
#             from data_loader import load_all_documents
#             docs = load_all_documents("data")
#             self.vectorstore.build_from_documents(docs)
#         else:
#             self.vectorstore.load()
#         groq_api_key = os.getenv("GROQ_API_KEY")
#         self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
#         print(f"[INFO] Groq LLM initialized: {llm_model}")

#     def search_and_summarize(self, query: str, top_k: int = 5) -> str:
#         results = self.vectorstore.query(query, top_k=top_k)
#         texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
#         context = "\n\n".join(texts)
#         if not context:
#             return "No relevant documents found."
#         prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""
#         response = self.llm.invoke([prompt])
#         return response.content

# # Example usage
# if __name__ == "__main__":
#     rag_search = RAGSearch()
#     query = "What is attention mechanism?"
#     summary = rag_search.search_and_summarize(query, top_k=3)
#     print("Summary:", summary)