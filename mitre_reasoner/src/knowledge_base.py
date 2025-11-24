import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_chroma import Chroma
from .embeddings import get_embedding_function
import os

class MitreKnowledgeBase:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_function = get_embedding_function()
        self.vectordb = None

    def load_from_csv(self, csv_path: str):
        """
        Ingests the MITREembed master CSV into ChromaDB.
        Adapted from MITREembed.ipynb
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        print(f"Loading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Ensure required columns exist (based on MITREembed structure)
        # Subject, Body, filepath, Source, Date
        # Note: 'Body' is used as the main content for embedding in MITREembed
        required_cols = ['Body', 'Subject', 'filepath', 'Source']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols}. Ensure CSV format matches MITREembed.")

        # Create Document Loader
        # In MITREembed, 'Body' is used as page_content
        loader = DataFrameLoader(df, page_content_column='Body')
        documents = loader.load()

        print(f"Creating vector store with {len(documents)} documents...")
        self.vectordb = Chroma.from_documents(
            documents=documents,
            embedding=self.embedding_function,
            persist_directory=self.persist_directory
        )
        # In newer Chroma versions, persist is automatic, but keeping for compatibility if needed
        # self.vectordb.persist() 
        print("Vector store created.")

    def load_existing(self):
        """Loads an existing persisted vector store."""
        print(f"Loading existing vector store from {self.persist_directory}...")
        self.vectordb = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function
        )
