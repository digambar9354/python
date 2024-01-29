import streamlit as st
import os
from streamlit_chat import message

from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

chat = ChatOpenAI(openai_api_key="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", temperature=0)

if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(
            content="You are a helpful assistant that helps to solve the user query."
        )
    ]

def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.user_input = ''
    st.session_state["messages"].append(
        HumanMessage(
            content=user_input
        )
    )
    
    systemMessage = chat(st.session_state["messages"])
    
    st.session_state["messages"].append(
        SystemMessage(
            content=systemMessage.content
        )
    )
    
    st.session_state.past.append(user_input)
    st.session_state.generated.append({'type': 'normal', 'data': systemMessage.content})

def on_btn_click():
    del st.session_state.past[:]
    del st.session_state.generated[:]

st.session_state.setdefault('past', [])
st.session_state.setdefault('generated', [])

st.title("AI Helper")

chat_placeholder = st.empty()

with chat_placeholder.container():    
    for i in range(len(st.session_state['generated'])):   
        message(st.session_state['past'][i], is_user=True, key=f"{i}_user")
        message(
            st.session_state['generated'][i]['data'], 
            key=f"{i}", 
            allow_html=True,
            is_table=True if st.session_state['generated'][i]['type']=='table' else False
        )

    if len(st.session_state['generated']) > 0:
        st.button("Clear message", on_click=on_btn_click)

with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
