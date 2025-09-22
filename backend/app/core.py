# backend/app/core.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def get_db_engine():
    # For deployment on Render, this will use the DATABASE_URL environment variable
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback for local development if DATABASE_URL isn't set
        db_password = os.getenv("DB_PASSWORD")
        if not db_password: raise ValueError("DB_PASSWORD or DATABASE_URL not found in .env")
        db_url = f"postgresql://postgres:{db_password}@localhost:5432/argo_data"
    return create_engine(db_url)

def get_llm():
    if not os.getenv("OPENROUTER_API_KEY"): raise ValueError("OPENROUTER_API_KEY not found in .env")
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={"HTTP-Referer": "argo-react-app-prod"}
    )

def get_vector_store():
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        persist_directory="chroma_db", 
        embedding_function=embedding_function,
        collection_name="argo_float_metadata"
    )
