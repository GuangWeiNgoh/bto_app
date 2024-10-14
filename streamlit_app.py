# app.py
import streamlit as st
from tabs import eligibility_checker, bto_assistant, about_us, methodology

# Set the page configuration
st.set_page_config(page_title="BTO App", layout="wide")

# Initialize session state for page tracking
if 'page' not in st.session_state:
    st.session_state.page = "BTO Eligibility Checker"

# Define button navigation in the sidebar
def navigate_to(page_name):
    st.session_state.page = page_name

# Create buttons for navigation
st.sidebar.header("Navigation")
if st.sidebar.button("🏠 BTO Eligibility Checker"):
    navigate_to("BTO Eligibility Checker")
if st.sidebar.button("✨ BTO Assistant"):
    navigate_to("BTO Assistant")
if st.sidebar.button("👥 About Us"):
    navigate_to("About Us")
if st.sidebar.button("📚 Methodology"):
    navigate_to("Methodology")

# Route to the selected page
if st.session_state.page == "BTO Eligibility Checker":
    eligibility_checker.display()
elif st.session_state.page == "BTO Assistant":
    bto_assistant.display()
elif st.session_state.page == "About Us":
    about_us.display()
elif st.session_state.page == "Methodology":
    methodology.display()
