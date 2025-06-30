import streamlit as st
from openai import OpenAI

st.title("Test OpenAI API Key")

try:
    # Initialize OpenAI client with your secret key
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.success("API key loaded successfully!")

    # Make a test request: create a simple embedding
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input="Hello, Streamlit!"
    )
    st.write("Embedding (first 5 values):", response.data[0].embedding[:5])

except Exception as e:
    st.error(f"Error: {e}")
