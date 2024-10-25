import streamlit as st
from openai import OpenAI
from crewai import Agent, Task, Crew
from crewai_tools import WebsiteSearchTool
from dotenv import load_dotenv

load_dotenv() 

# Initialize the OpenAI client with the API key from Streamlit secrets
client = OpenAI(
    api_key=st.secrets["openai"]["api_key"],
)

# Set up the website search tool to scrape data from the HDB website
tool_websearch = WebsiteSearchTool("https://www.hdb.gov.sg/")

# Agent: Question Planner
agent_question_planner = Agent(
    role="Question Planner",
    goal="Plan how to answer the user question about Singapore HDB: {question}",
    backstory="Your task is to break down the question into key areas related to Singapore HDB that need research.",
    allow_delegation=False,
    verbose=True,
)

# Agent: Research Analyst
agent_researcher = Agent(
    role="Research Analyst",
    goal="Conduct research to answer the question: {question}",
    backstory="You will gather information from the Singapore HDB website to provide accurate answers about Singapore HDB flats.",
    allow_delegation=False,
    verbose=True,
)

# Agent: Answer Writer
agent_answer_writer = Agent(
    role="Answer Writer",
    goal="Write a clear and concise answer to the question: {question}",
    backstory="Based on the research, you will compile the findings into a structured answer.",
    allow_delegation=False,
    verbose=True,
)

# Task: Plan the question breakdown
task_plan = Task(
    description="""\
    1. Break down the user question into sub-questions or key areas related to Singapore HDB.
    2. Identify the main topics needed to answer the question (e.g., eligibility, process, costs, etc.).""",
    expected_output="""\
    An outline of the key areas to address in the answer related to Singapore HDB.""",
    agent=agent_question_planner,
    async_execution=True
)

# Task: Research the answer by gathering information from the HDB website
task_research = Task(
    description="""\
    1. Conduct research on the HDB website about the user question on Singapore HDB.
    2. Gather relevant information (eligibility, application process, pricing, etc.).
    3. Provide a summary of the findings that will help answer the user’s question.""",
    expected_output="""\
    A detailed research report with key information about Singapore HDB from the website.""",
    agent=agent_researcher,
    tools=[tool_websearch],  # Using the web scraping tool to search and gather data
    async_execution=True
)

# Task: Write the final answer based on research
task_write = Task(
    description="""\
    1. Use the research findings to write a clear and accurate answer to the user question.
    2. Structure the answer with an introduction, key points (eligibility, process, etc.), and a conclusion.
    3. Ensure the answer is easy to understand and factually correct.""",
    expected_output="""\
    A concise, structured answer to the user question about Singapore HDB.""",
    agent=agent_answer_writer,
    context=[task_plan, task_research],  # The writer depends on the planner and researcher tasks
    output_file="bto_answer.txt"
)

# Create the crew of agents
crew = Crew(
    agents=[agent_question_planner, agent_researcher, agent_answer_writer],
    tasks=[task_plan, task_research, task_write], 
    verbose=True
)

# Function to display the chatbot
def display():
    st.title("✨ HDB Assistant")
    st.write("Get assistance with your HDB questions from GPT 3.5 Turbo & information straight from HDB's website.")

    # Initialize session state for messages if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Function to display the chat messages
    def display_messages(input):
        st.markdown(
                    f"""
                    <div style="border: 1px solid #FFD700; border-radius: 8px; padding: 10px; margin: 10px 0; background-color: transparent;">
                        <strong style="color: #FFD700;">You:</strong> <span style="color: #FFD700;">{input}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    user_input = st.text_area("Ask your question about BTO:", placeholder="E.g., What are the new BTO launches in 2025?")

    if st.button("Submit"):
        if user_input:

            display_messages(user_input)

            with st.spinner("Getting GPT response..."):
                try:

                    prompt = f"""
                    Please read the following query and strictly focus on Singapore HDB related information only. Strictly do not respond if it is not relatedto HDB.
                    <user_input>
                    ``` 
                    {user_input}
                    ``` 
                    </user_input>
                    Please provide a structured answer based on the above question. Your response should only contain information specific to the above question. Ensure your answer starts with "Answer: ".
                    """

                    # Append the user's message to the conversation history
                    st.session_state.messages.append({"role": "user", "content": prompt})

                    # Make a request to OpenAI using ChatCompletion
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=st.session_state.messages
                    )

                    # Extract and display the assistant's response
                    assistant_response = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                except Exception as e:
                    st.error(f"An error occurred with GPT: {e}")

            # Display updated messages after getting GPT response
            with st.expander("GPT Response", expanded=True):
                st.markdown(assistant_response)

            with st.spinner("Getting Crew Web Search response..."):
                try:
                    # Function to execute the agent workflow and return the answer
                    def get_hdb_bto_answer(question):
                        result = crew.kickoff(inputs={"question": question})
                        with open("bto_answer.txt", "r") as file:
                            return file.read()   
                        
                    # Call the function to get the answer
                    websearch_response = get_hdb_bto_answer(prompt)

                    # Add the web search results to the assistant's response
                    st.session_state.messages.append({"role": "assistant", "content": "Additional info from HDB:\n" + websearch_response})

                except Exception as e:
                    st.error(f"An error occurred with Crew Web Search: {e}")

            # Display the GPT response and web search response in collapsible sections
            with st.expander("Additional Info from HDB", expanded=True):
                st.markdown(websearch_response)
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    display()