import streamlit as st

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from tabs import eligibility_checker, about_us, hdb_assistant, methodology, resale_transactions_explorer

from utility import check_password

# Do not continue if check_password is not True.  
#if not check_password():  
#    st.stop()

# Set the page configuration
st.set_page_config(page_title="HDB Explorer", layout="wide")

# Initialize session state for page tracking
if 'page' not in st.session_state:
    st.session_state.page = "HDB Resale Transactions Explorer"

# Add disclaimer using an expander
with st.expander("Disclaimer", expanded=False):
    st.write("""
    IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. 
    The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

    Always consult with qualified professionals for accurate and personalized advice.
    """)

# Define button navigation in the sidebar
def navigate_to(page_name):
    st.session_state.page = page_name

# Create buttons for navigation
st.sidebar.header("Navigation")
if st.sidebar.button("🏠 HDB Resale Transactions Explorer"):
    navigate_to("HDB Resale Transactions Explorer")
if st.sidebar.button("✨ HDB Assistant"):
    navigate_to("HDB Assistant")
# if st.sidebar.button("🏠 BTO Eligibility Checker"):
#     navigate_to("BTO Eligibility Checker")
if st.sidebar.button("👥 About Us"):
    navigate_to("About Us")
if st.sidebar.button("📚 Methodology"):
    navigate_to("Methodology")

# Route to the selected page
if st.session_state.page == "HDB Resale Transactions Explorer":
    resale_transactions_explorer.display()
elif st.session_state.page == "HDB Assistant":
    hdb_assistant.display()
elif st.session_state.page == "BTO Eligibility Checker":
    eligibility_checker.display()
elif st.session_state.page == "About Us":
    about_us.display()
elif st.session_state.page == "Methodology":
    methodology.display()
