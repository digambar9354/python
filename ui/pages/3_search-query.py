import streamlit as st
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain
from langchain.chains.question_answering import load_qa_chain

from dotenv import load_dotenv
from pathlib import Path

import os

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_searched_documents(query):
    if "sharedsearch" in st.session_state:
        docs = st.session_state["sharedsearch"].similarity_search(query, k=3)
        st.write("##### Similarity search")
        st.write(docs)
        return docs
    else: 
        return ''
    
def get_ai_result(docs, query):
    # st.write("### docs")
    # st.write(docs)
    chain = load_qa_chain(ChatOpenAI(), chain_type="stuff")
    result = chain.run(input_documents=docs, question=query)
    st.write("### chain")
    st.write(chain)
    return result

def character_text_splitter(content, search):
    text_splitter = CharacterTextSplitter(
        separator="\n\n\t\t",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
        keep_separator=True
    )
    metadatas = [{"title": search}]

    documents = text_splitter.create_documents([content], metadatas=metadatas)
    return documents

def main():
    st.markdown("# Search")
    st.sidebar.markdown("# Search")

    # Document title
    query = st.text_input("Enter the query")

    if st.button("Search", key=None, help=None, on_click=None, args=None, kwargs=None, type="secondary", disabled=False, use_container_width=False): 
        doc = get_searched_documents(query)

        output = get_ai_result(doc, query)
        st.write("#### Output:")
        if output:
            st.write(output)
        else:
            st.error(f"Document not found")

if __name__ == "__main__":
    main()
