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


def connect_table(database):
    try:
        db = lancedb.connect("~/.lancedb")
        # if database == 'lancedb':
        #     db = lancedb.connect("./data/my_db")
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
                "id": "1",
            }
        ],
        mode="overwrite",
    )
    return table

def store_embeddings(query):
    db = lancedb.connect("~/.lancedb")
    table = db.open_table("recipes")
    
    table.search(query)
    # docsearch = LanceDB.from_documents(table.get_text, OpenAIEmbeddings(), connection=table)
    # docs = docsearch.similarity_search(query)
    return st.error(f"docs: {table.search(query)}")

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
            content = read_pdf(file.name)  # Assuming file.name contains the temporary path
        except FileNotFoundError as e:
            st.error(f"Error reading PDF file: {e}")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content = read_docx(file)
    
    return content

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

    # Document title
    document_title = st.text_input("Enter the document title:")

    if st.button("Search", key=None, help=None, on_click=None, args=None, kwargs=None, type="secondary", disabled=False, use_container_width=False): 
        store_embeddings(document_title)

if __name__ == "__main__":
    main()
