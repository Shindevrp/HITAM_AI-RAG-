import os
import numpy as np
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from creds import openai_key, PINECONE_API_KEY, index_name


class DocumentLoader:
    def __init__(self, files):
        self.files = files

    def load_documents(self):
        documents = []
        for file in self.files:
            name, extension = os.path.splitext(file)
            if extension == '.pdf':
                print(f'Loading {file}')
                loader = PyPDFLoader(file)
            elif extension == '.docx':
                print(f'Loading {file}')
                loader = Docx2txtLoader(file)
            elif extension == '.txt':
                loader = TextLoader(file)
            else:
                print(f'Document format of {file} is not supported!')
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
            print("The 'embed_documents' method returned None. Please check your code and the documentation.")
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


if __name__ == "__main__":
    # Load documents
    document_paths = [
        r"C:\Users\Shinde dev rao patil\Desktop\hitam_ai\entrepreneurship-cell-data.pdf",
        r"C:\Users\Shinde dev rao patil\Desktop\hitam_ai\Final-Updated-COURSE-STRUCTURE-V5.pdf",
        r"C:\Users\Shinde dev rao patil\Desktop\hitam_ai\HITAM  (2).pdf"
    ]
    doc_loader = DocumentLoader(document_paths)
    documents = doc_loader.load_documents()

    # Process each document
    chunk_processor = ChunkProcessor()
    embedding_processor = EmbeddingProcessor(openai_api=openai_key)
    pinecone_uploader = PineconeUploader(pinecone_api=PINECONE_API_KEY, index_name=index_name)

    for doc in documents:
        # Chunk data
        chunks = chunk_processor.chunk_data(doc)

        # Embedding
        embedding_response = embedding_processor.chunk_embedding(chunks)

        # Pinecone upload
        for single_data in embedding_response:
            pinecone_uploader.upsert_data(data=[single_data])
        print(f"--------------DATA FROM {doc} UPLOADED TO PINECONE SUCCESSFULLY----------------")

    # After uploading all documents
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)
    print("----------------PINECONE INDEX STATS--------------------")
    print(index.describe_index_stats())
