import streamlit as st
from openai import OpenAI
from openai._exceptions import OpenAIError
import faiss
import numpy as np

# Load FAQ from txt file and parse Q&A pairs
def load_faq(file_path="faq.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    faqs = []
    items = content.strip().split("\n\n")
    for item in items:
        lines = item.strip().split("\n")
        question = lines[0].strip()
        answer = " ".join(line.strip() for line in lines[1:])
        faqs.append({"question": question, "answer": answer})
    return faqs

# Embed FAQ questions using OpenAI embeddings
def embed_questions(questions, client):
    embeddings = []
    for q in questions:
        response = client.embeddings.create(
            input=q,
            model="text-embedding-3-large"
        )
        emb = response.data[0].embedding
        embeddings.append(emb)
    return np.array(embeddings).astype("float32")

# Setup FAISS index
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Get answer for user query
def get_answer(user_query, client, faq_data, index, model):
    try:
        # Embed user query
        query_response = client.embeddings.create(
            input=user_query,
            model="text-embedding-3-large"
        )
        query_embedding = np.array(query_response.data[0].embedding).astype("float32").reshape(1, -1)

        # Search FAISS for closest question
        D, I = index.search(query_embedding, k=1)
        matched_idx = I[0][0]
        matched_answer = faq_data[matched_idx]["answer"]

        # Call OpenAI chat to generate a response based on matched answer and user query
        chat_response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use only the context given to answer the question."
                },
                {
                    "role": "user",
                    "content": f"Context: {matched_answer}\n\nQuestion: {user_query}"
                }
            ],
        )
        return chat_response.choices[0].message.content

    except OpenAIError as e:
        return f"⚠️ OpenAI API Error: {str(e)}"


# Streamlit UI
st.set_page_config(page_title="FlexCrew FAQ Chatbot", page_icon="📚")

st.title("📚 FlexCrew FAQ Chatbot")
st.write("Ask me anything from the FAQ!")

# Load FAQ data
faq_data = load_faq()
questions = [item["question"] for item in faq_data]

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Embed questions and create FAISS index once and cache results for performance
@st.cache_resource(show_spinner=False)
def get_index_and_model():
    embeddings = embed_questions(questions, client)
    index = create_faiss_index(embeddings)
    model_name = "gpt-3.5-turbo"  # Use an available model for chat completion
    return index, model_name

index, model = get_index_and_model()

# Input box for user query
user_input = st.text_input("Your question:")

if user_input:
    answer = get_answer(user_input, client, faq_data, index, model)
    st.markdown(f"**Answer:** {answer}")
