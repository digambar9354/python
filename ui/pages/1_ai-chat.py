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

os.environ["LANGCHAIN_API_KEY"] = "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"
chat = ChatOpenAI(temperature=0)
messages = []

def on_input_change():
    user_input = st.session_state.user_input

    if len(st.session_state.generated) > 0:
        messages.append(
            SystemMessage(
                content="You are a helpful assistant that helps to solve the user query."
            )
        )

    messages.append(
        HumanMessage(
            content=user_input
        )
    )
    
    
    systemMessage = chat(messages)
    
    
    messages.append(
        SystemMessage(
            content=systemMessage.content
        )
    )
    
    st.write("### chat  messages:")
    st.write(systemMessage)
    
    st.session_state.past.append(user_input)
    st.session_state.generated.append({'type': 'normal', 'data': 'The messages from Bot\nWith new line'})

def on_btn_click():
    del st.session_state.past[:]
    del st.session_state.generated[:]

st.session_state.setdefault('past', [])
st.session_state.setdefault('generated', [])

st.title("Chat placeholder")

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
    
    st.button("Clear message", on_click=on_btn_click)

with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
