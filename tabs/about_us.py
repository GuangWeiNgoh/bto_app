import streamlit as st

def display():

    st.title("👥 About Us")

    # Application Title
    st.header("🏠 HDB Resale Transactions Explorer")

    # Project Scope for Resale Transactions Explorer
    with st.expander("Scope", expanded=True):
        st.write("""
        The HDB Resale Transactions Explorer is a web application designed to facilitate the exploration and analysis of 
        Housing Development Board (HDB) resale flat transactions in Singapore. The application provides users with an 
        interactive interface to view, filter, and visualize resale data spanning from 1990 to the present. By leveraging 
        data from (https://data.gov.sg/), the official government data portal for Singapore, the project aims to enhance public access to real estate information, aiding potential buyers, 
        researchers, and policy-makers in their decision-making processes.
        """)

    # Objectives for Resale Transactions Explorer
    with st.expander("Objectives", expanded=True):
        st.markdown("""
        - **Data Accessibility:** Enable users to access comprehensive resale flat transaction data, enhancing transparency 
        in the real estate market.
        
        - **Interactive Data Visualization:** Provide visual representations of key metrics (e.g., average resale prices 
        by town or flat type) to facilitate understanding of market trends.
        
        - **Customizable Data Filters:** Allow users to filter data based on various criteria (e.g., year, month, town, 
        flat type) for tailored insights.
        
        - **Data Updates:** Implement a mechanism to update the dataset easily, ensuring users have access to the most 
        current data.
        
        - **User-Friendly Interface:** Design an intuitive and responsive interface that guides users through the data 
        exploration process.
        """)

    # Data Sources for Resale Transactions Explorer
    with st.expander("Data Sources", expanded=True):
        st.write("""\
            The primary data source for this project is the (https://data.gov.sg/) API, which provides access to public datasets, including 
            detailed information on HDB resale transactions.  
        """)
        st.markdown("The data includes attributes such as:")

        st.markdown("""
        - **Month of transaction**
        - **Town where the flat is located**
        - **Flat type and model**
        - **Block and street names**
        - **Storey range and floor area**
        - **Lease commence date and remaining lease period**
        - **Resale price**
        """)

    # Features for Resale Transactions Explorer
    with st.expander("Features", expanded=True):
        st.markdown("""
        - **Data Loading and Caching:** The application first checks for a locally stored ZIP file containing the dataset. 
        If it exists, it loads the data from the ZIP file; otherwise, it fetches the latest data from the API. The fetched 
        data is serialized and stored in a ZIP file using a highly compressed format to optimize storage.
        
        - **Data Visualization:** 
            - **Bar Charts:** Users can view average resale prices by town and flat type using Altair bar charts, providing 
            a visual representation of market conditions.
            - **Line Chart:** The application also features a line chart illustrating how average resale prices change over 
            the years.
        
        - **Dynamic Filtering:** Users can select specific years, months, towns, flat types, storey ranges, and other 
        attributes to filter the dataset dynamically. Sliders allow for range selections on numeric values such as 
        floor area, remaining lease, lease commence date, and resale price.
        
        - **User Interface Elements:** Interactive buttons and message placeholders guide users in updating data and provide 
        feedback (e.g., success messages) regarding actions taken. The application employs a responsive layout using 
        Streamlit columns to organize the filter options efficiently.
        
        - **Error Handling:** The application includes error handling to manage issues such as failed data fetch attempts, 
        ensuring a robust user experience.
        
        - **Session State Management:** The use of Streamlit’s session state enables the application to maintain user 
        selections and data across interactions, enhancing usability.
        """)

    # HDB Assistant Project Overview
    st.header("✨ HDB Assistant")

    # Project Scope for HDB Assistant
    with st.expander("Scope", expanded=True):
        st.write("""
        The project aims to create a web application using Streamlit that serves as an interactive assistant for answering questions related to Singapore's Housing and Development Board (HDB) flats. 
        The application integrates natural language processing (NLP) capabilities from OpenAI's GPT model and web scraping tools to gather accurate and up-to-date information directly from the HDB official website.
        """)

    # Objectives for HDB Assistant
    with st.expander("Objectives", expanded=True):
        objectives = [
            "Provide Accurate Information: Enable users to obtain reliable and precise answers to their HDB-related queries, such as eligibility, application processes, and pricing.",
            "Enhance User Experience: Create a user-friendly interface that allows users to ask questions easily and receive structured answers quickly.",
            "Leverage AI and Web Scraping: Combine the capabilities of AI for understanding user questions and web scraping for retrieving the latest data from the HDB website.",
            "Facilitate Learning: Educate users about HDB processes, helping them navigate the complexities of housing in Singapore."
        ]
        for objective in objectives:
            st.markdown(f"- {objective}")

    # Data Sources for HDB Assistant
    with st.expander("Data Sources", expanded=True):
        data_sources = [
            "HDB Official Website: The primary data source for gathering information is the official HDB website (https://www.hdb.gov.sg/), where the application will scrape relevant content related to user inquiries.",
            "OpenAI API: The application utilizes the OpenAI GPT model to generate responses based on user questions and the data retrieved from the HDB website."
        ]
        for source in data_sources:
            st.markdown(f"- {source}")

    # Features for HDB Assistant
    with st.expander("Features", expanded=True):
        features = [
            "User Input Section: A text area for users to submit their questions related to HDB, with a placeholder for guidance.",
            "Question Breakdown: An agent (Question Planner) that breaks down the user’s query into sub-questions or key areas of focus, ensuring thoroughness in research.",
            "Research and Information Gathering: A second agent (Research Analyst) that conducts a web search using the WebsiteSearchTool to gather relevant information from the HDB website based on the breakdown provided by the Question Planner.",
            "Structured Response Generation: A third agent (Answer Writer) that synthesizes the gathered information into a clear, structured answer that addresses the user’s question comprehensively.",
            "Chat Interface: A chat interface that displays user queries and responses from the assistant, enhancing interactivity.",
            "Loading Indicators: Visual indicators (spinners) to inform users that responses are being generated, improving the user experience.",
            "Collapsible Sections: Expandable sections to display responses from both the OpenAI model and the Crew Web Search, allowing users to access detailed information without overwhelming the interface.",
            "Error Handling: Error messages that inform users if issues arise during the question-answering process, maintaining clarity and functionality."
        ]
        for feature in features:
            st.markdown(f"- {feature}")

if __name__ == "__main__":
    display_project_overview()
