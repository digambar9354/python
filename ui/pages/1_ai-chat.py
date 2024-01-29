import streamlit as st
from streamlit_chat import message

from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import dotenv_values

config = dotenv_values(".env")

OPENAI_API_KEY=config.OPENAI_API_KEY

chat = ChatOpenAI(temperature=0)

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
    del st.session_state.messages[:]
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

    if len(st.session_state['generated']) >= 1:
        st.button("Clear message", on_click=on_btn_click)

with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
