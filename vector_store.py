from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class VectorStore:
    def __init__(self, api_key):
        self.text_splitter = CharacterTextSplitter(chunk_size=512, chunk_overlap=0)
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.vector_store = None

    def create_vector_store(self, text):
        chunks = self.text_splitter.split_text(text)
        self.vector_store = FAISS.from_texts(chunks, self.embeddings)

    def similarity_search(self, query, k=4):
        if not self.vector_store:
            return []
        return self.vector_store.similarity_search(query, k=k)