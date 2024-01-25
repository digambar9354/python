import streamlit as st
import docx2txt
import fitz
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import LanceDB

import lancedb
os.environ["LANGCHAIN_API_KEY"] = "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"

def get_embeddings(query):
    if "sharedsearch" in st.session_state:
        st.write(st.session_state["sharedsearch"])
        docs = st.session_state["sharedsearch"].similarity_search(query)
        return docs[0].page_content
    else: 
        return st.error(f"docs not found")

def character_text_splitter(content, document_title):
    text_splitter = CharacterTextSplitter(
        separator="\n\n\t\t",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
        keep_separator=True
    )
    metadatas = [{"title": document_title}]

    documents = text_splitter.create_documents([content], metadatas=metadatas)
    return documents

def main():
    
    st.markdown("# Search")
    st.sidebar.markdown("# Search")

    # Document title
    document_title = st.text_input("Enter the document title:")

    if st.button("Search", key=None, help=None, on_click=None, args=None, kwargs=None, type="secondary", disabled=False, use_container_width=False): 
        
        result = get_embeddings(document_title)
        
        st.write("#### Output:")
        st.write(result)
        

if __name__ == "__main__":
    main()
