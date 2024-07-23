from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

class Chatbot:
    def __init__(self, vector_store, api_key):
        self.vector_store = vector_store
        self.llm = ChatOpenAI(temperature=0, openai_api_key=api_key)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            retriever=self.vector_store.vector_store.as_retriever(),
            memory=self.memory
        )

    def chat(self, query):
        response = self.chain({"question": query})
        return response['answer']