import streamlit as st
import docx2txt
import fitz
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.vectorstores import LanceDB

import lancedb
import os

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def connect_table(database):
    try:
        if database == 'lancedb':
            db = lancedb.connect("~/.lancedb")
        return db
    except Exception as e:
        return st.error(f"Error during LanceDB operations: {e}")

def create_table(db): 
    table = db.create_table(
        "recipes",
        data=[
            {
                "vector": OpenAIEmbeddings().embed_query("Recipes"),
                "text": "Recipes",
            }
        ],
        mode="overwrite",
    )
    return table

def store_embeddings(content, document_title):
    try:
        db = connect_table("lancedb")
        table = create_table(db)

        documents = character_text_splitter(content, document_title)
        docsearch = LanceDB.from_documents(documents, OpenAIEmbeddings(), connection=table)

        if "sharedsearch" not in st.session_state:
            st.session_state["sharedsearch"] = docsearch

        query = "Get METHOD for Aloo Palak"

        # ->>>> similarity_search
        docs = docsearch.similarity_search(query, k=1, score=True)
        st.write(docs)

        # ->>>> similarity_search_by_vector
        # embedding_vector = OpenAIEmbeddings().embed_query(query)
        # docs = docsearch.max_marginal_relevance_search(embedding_vector, k=2, fetch_k=10)

        # found_docs = docs.amax_marginal_relevance_search(query, k=2, fetch_k=10)
        # for i, doc in enumerate(found_docs):
        #     print(f"{i + 1}.", doc.page_content, "\n")
        return docs
    except FileNotFoundError as e:
        st.error(f"Error while Storing Embeddings: {e}")

def read_docx(file_path):
    text = docx2txt.process(file_path)
    return text

def read_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")

    pdf_document = fitz.open(file_path)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        text += page.get_text()
    return text

def read_file(file):
    content = ""

    if file.type == "application/pdf":
        try:
            content = read_pdf(file.name)
        except FileNotFoundError as e:
            st.error(f"Error reading PDF file: {e}")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = read_docx(file)
    
    formatted_text = content.upper()
    return formatted_text

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
    st.markdown("# File Upload")
    st.sidebar.markdown("# File Upload")

    document_title = st.text_input("Enter the document title:")
    uploaded_file = st.file_uploader("Upload a document (doc, pdf) or provide a link", type=["docx", "pdf"])

    if uploaded_file is not None:
        try:
            content = read_file(uploaded_file)
            documents = store_embeddings(content, document_title)
            st.write("### Content:")
            st.write(documents)
        except FileNotFoundError as e:
            st.error(f"Error reading content from the uploaded file: {e}")
            
if __name__ == "__main__":
    main()
