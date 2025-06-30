import streamlit as st
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import faiss
import os

# Load OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Load FAQs from file
def load_faq(filepath="faq.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    faqs = content.strip().split("\n\n")
    data = []
    for faq in faqs:
        if "\n" in faq:
            q, a = faq.split("\n", 1)
            data.append({"question": q.strip(), "answer": a.strip()})
    return data

faq_data = load_faq()

# Embed questions using SentenceTransformer
@st.cache_resource
def embed_questions(faq_data):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    questions = [item["question"] for item in faq_data]
    embeddings = model.encode(questions)
    index = faiss.IndexFlatL2(embeddings[0].shape[0])
    index.add(embeddings)
    return model, index, questions

model, index, questions = embed_questions(faq_data)

# Function to get the most relevant answer
def get_answer(user_query):
    query_embedding = model.encode([user_query])
    D, I = index.search(query_embedding, k=1)
    closest_q_idx = I[0][0]
    context = faq_data[closest_q_idx]["answer"]

    # Call OpenAI Chat API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful support assistant. Answer based only on the provided context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_query}"}
        ]
    )
    return response.choices[0].message.content

# Streamlit app UI
st.set_page_config(page_title="FAQ Chatbot")
st.title("📚 FlexCrew FAQ Chatbot")
st.write("Ask me anything from the FAQ!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Chat input
user_input = st.chat_input("Type your question here...")

if user_input:
    with st.spinner("Thinking..."):
        answer = get_answer(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", answer))

# Display chat history
for sender, msg in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(msg)
