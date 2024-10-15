# pages/bto_assistant.py
import streamlit as st
from openai import OpenAI

# Initialize the OpenAI client with the API key from Streamlit secrets
client = OpenAI(
    api_key=st.secrets["openai"]["api_key"],
)

def display():
    st.title("✨ BTO Assistant")
    st.write("Get assistance with your BTO application.")

    # Initialize session state for messages if it doesn't exist
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Function to display the chat messages
    def display_messages():
        # Loop through the messages in reverse order
        for message in reversed(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div style="border: 1px solid white; border-radius: 8px; padding: 10px; margin: 10px 0; background-color: transparent;">
                        <strong>You:</strong> {message['content']}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="border: 1px solid #FFD700; border-radius: 8px; padding: 10px; margin: 10px 0; background-color: transparent;">
                        <strong style="color: #FFD700;">Assistant:</strong> <span style="color: #FFD700;">{message['content']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Display existing chat messages
    # display_messages()

    user_input = st.text_area("Ask your question:")
    
    if st.button("Submit"):
        if user_input:
            with st.spinner("Getting response..."):
                try:
                    # Append the user's message to the conversation history
                    st.session_state.messages.append({"role": "user", "content": user_input})

                    # Make a request to OpenAI using ChatCompletion
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",  # Ensure you're using a valid model
                        messages=st.session_state.messages
                    )
                    
                    # Extract and display the assistant's response
                    assistant_response = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                    # Display the updated messages
                    display_messages()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a question.")

# This is a typical structure for a Streamlit app
if __name__ == "__main__":
    display()
