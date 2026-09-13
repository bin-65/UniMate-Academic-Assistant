import os
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import EMBEDDING_MODEL_NAME, VECTOR_STORE_PATH

class RAGEngine:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        self.vector_store = None
        self._load_existing_index()

    def _load_existing_index(self):
        if os.path.exists(VECTOR_STORE_PATH):
            try:
                self.vector_store = FAISS.load_local(
                    VECTOR_STORE_PATH, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
            except Exception:
                self.vector_store = None

    def process_and_index_pdfs(self, pdf_file_paths: List[str]) -> int:
        all_docs = []
        for file_path in pdf_file_paths:
            loader = PyPDFLoader(file_path)
            all_docs.extend(loader.load())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )
        chunks = text_splitter.split_documents(all_docs)

        if chunks:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            self.vector_store.save_local(VECTOR_STORE_PATH)
            return len(chunks)
        return 0

    def retrieve_context(self, query: str, k: int = 3) -> Tuple[str, List[str]]:
        if not self.vector_store:
            return "", []

        docs = self.vector_store.similarity_search(query, k=k)
        context_str = "\n\n".join([doc.page_content for doc in docs])
        sources = list(set([
            f"{os.path.basename(doc.metadata.get('source', 'Unknown'))} (Page {doc.metadata.get('page', 0) + 1})"
            for doc in docs
        ]))
        return context_str, sources
