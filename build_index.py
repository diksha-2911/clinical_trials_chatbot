from src.clinical_trials_loader import load_clinical_trials
from src.vectorstore import FaissVectorStore

docs = load_clinical_trials("data/trials.json")

store = FaissVectorStore("faiss_store")

store.build_from_documents(docs)

print("FAISS index built successfully.")