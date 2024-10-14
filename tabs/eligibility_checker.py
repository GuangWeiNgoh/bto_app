# pages/eligibility_checker.py
import streamlit as st

def display():
    st.title("🏠 BTO Eligibility Checker")
    st.write("Check your eligibility for BTO flats here.")
    st.text_input("Enter your information:")
    st.button("Check Eligibility")
