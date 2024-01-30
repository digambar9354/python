from langchain_openai import ChatOpenAI
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec

from langchain.chains import RetrievalQA

import os

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")

# st.write(PINECONE_API_KEY)
# st.write(PINECONE_ENV)
def main():
    st.sidebar.markdown("# Pinecone")

    if "sharedsearch" in st.session_state:
        st.write(st.session_state["sharedsearch"])

    pc = Pinecone(api_key=PINECONE_API_KEY,environment=PINECONE_ENV)
    index = pc.Index("recipes")

    if "sharedsearch" in st.session_state:
        st.write(details)
        index.upsert(
            vectors=[('a', st.write(st.session_state["sharedsearch"]))]
        )

    details = index.fetch(ids=['a'], namespace="ns1")
    st.write("### Pinecone:")
    st.write(details)


if __name__ == "__main__":
    main()
