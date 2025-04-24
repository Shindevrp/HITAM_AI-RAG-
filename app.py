import streamlit as st
import os
import numpy as np
import sqlite3
from datetime import datetime
import uuid  # Import uuid module
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from creds import openai_key, PINECONE_API_KEY, index_name
from langchain_community.callbacks import get_openai_callback
from langchain_openai import OpenAI
from langchain.chains import ConversationalRetrievalChain
import langchain.globals as globals

class TokenCountCallback:
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.successful_requests = 0
        self.total_cost_usd = 0

    def update_callback_details(self, callback):
        self.total_tokens += callback.total_tokens
        self.prompt_tokens += callback.prompt_tokens
        self.completion_tokens += callback.completion_tokens
        self.successful_requests += 1
        # Approximate cost based on the number of tokens used
        self.total_cost_usd += callback.total_tokens * 0.0001  # Example cost per token, adjust as needed

class DocumentLoader:
    def __init__(self, files):
        self.files = files

    def load_documents(self):
        documents = []
        for file in self.files:
            name, extension = os.path.splitext(file)
            if extension == '.pdf':
                loader = PyPDFLoader(file)
            elif extension == '.docx':
                loader = Docx2txtLoader(file)
            elif extension == '.txt':
                loader = TextLoader(file)
            else:
                st.write(f'Document format of {file} is not supported!')
                continue
            document = loader.load()
            if document:
                documents.append(document)
        return documents

class ChunkProcessor:
    def __init__(self, chunk_size=256):
        self.chunk_size = chunk_size

    def chunk_data(self, data):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=10)
        chunks = text_splitter.split_documents(data)
        chunk_list = [chunk.page_content for chunk in chunks]
        return chunk_list

class EmbeddingProcessor:
    def __init__(self, openai_api):
        self.openai_api = openai_api

    def chunk_embedding(self, chunks):
        embeddings = OpenAIEmbeddings(api_key=self.openai_api, model="text-embedding-ada-002")
        embeddings_list = embeddings.embed_documents(chunks)
        if embeddings_list is None:
            st.write("The 'embed_documents' method returned None. Please check your code and the documentation.")
            return {"status": False}
        return_data = []
        id = 1
        for chunk, embedding in zip(chunks, embeddings_list):
            reshaped_embedding = np.array(embedding).reshape(1, 1536)
            return_data.append(
                {
                    "id": str(id),
                    "metadata": {"chunk": chunk},
                    "values": reshaped_embedding.tolist()[0]
                }
            )
            id += 1
        return return_data

class PineconeUploader:
    def __init__(self, pinecone_api, index_name):
        self.pinecone_api = pinecone_api
        self.index_name = index_name

    def upsert_data(self, data):
        pc = Pinecone(api_key=self.pinecone_api)
        index = pc.Index(self.index_name)
        index.upsert(vectors=data)
        return {"status": True, "message": "data uploaded"}

def create_database():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id TEXT PRIMARY KEY, timestamp TEXT, question TEXT, answer TEXT, token_count INTEGER)''')
    conn.commit()
    conn.close()

def insert_chat_history(question, answer, token_count):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    entry_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO chat_history (id, timestamp, question, answer, token_count) VALUES (?, ?, ?, ?, ?)",
              (entry_id, timestamp, question, answer, token_count))
    conn.commit()
    conn.close()

def get_chat_history():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM chat_history")
    history = c.fetchall()
    conn.close()
    return history

def track_token_usage(llm, text, token_count_callback):
    with get_openai_callback() as cb:
        llm.invoke(text)
    token_count_callback.update_callback_details(cb)
    return cb.total_tokens

create_database()
llm = OpenAI(temperature=0, openai_api_key=openai_key)  
token_count_callback = TokenCountCallback()

# Set verbosity level
globals.set_verbose(True)

# Instantiate objects
chat = ChatOpenAI(temperature=0, openai_api_key=openai_key, model="gpt-3.5-turbo-0125")
embeddings = OpenAIEmbeddings(api_key=openai_key, model="text-embedding-ada-002")
vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings, 
                                  pinecone_api_key=PINECONE_API_KEY, text_key="chunk")
retriever = vectorstore.as_retriever(search_kwargs={'k': 3})
chain = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever)

st.title("Chat History")

# Display chat history
history = get_chat_history()
if history:
    st.subheader("Chat History")
    for entry in history:
        st.write(entry)
else:
    st.write("No chat history available.")

# Allow user to interact
user_input = st.text_input("User:")
chat_history = get_chat_history()
if user_input:
    total_tokens = track_token_usage(llm, user_input, token_count_callback)
    result = chain.invoke({"question": user_input, "chat_history": chat_history})
    st.write("Bot:", result)
    insert_chat_history(user_input, result, total_tokens)
