# pages/bto_assistant.py
import streamlit as st

def display():
    st.title("✨ BTO Assistant")
    st.write("Get assistance with your BTO application.")
    st.text_area("Ask your question:")
    st.button("Submit")
