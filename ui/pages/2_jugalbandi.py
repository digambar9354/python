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

def main():
    st.markdown("# Jugalbandi")
    st.sidebar.markdown("# Jugalbandi")

if __name__ == "__main__":
    main()
