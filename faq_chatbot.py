import streamlit as st
import openai
import faiss
import numpy as np
import re
from sentence_transformers import SentenceTransformer

# Load OpenAI API key from Streamlit secrets (set in .streamlit/secrets.toml)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="FAQ Chatbot", layout="centered")
st.title("🤖 FAQ Chatbot")
st.write("Ask a question and get an answer based on your FAQ document.")

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

def parse_faq(text):
    """
    Parse FAQ text with format like:
    1. Question?
    Answer...

    2. Question?
    Answer...
    """
    # Split on numbered question pattern
    entries = re.split(r'\n\d+\.\s', text.strip())
    faq_pairs = []
    for entry in entries:
        if entry.strip() == "":
            continue
        # Split question and answer by first newline
        parts = entry.split('\n', 1)
        if len(parts) == 2:
            question = parts[0].strip()
            answer = parts[1].strip()
            faq_pairs.append((question, answer))
        else:
            faq_pairs.append((parts[0].strip(), ""))
    return faq_pairs

@st.cache_data
def load_faq(faq_file):
    with open(faq_file, "r", encoding="utf-8") as f:
        text = f.read()
    faq_pairs = parse_faq(text)
    faq_texts = [q + " " + a for q, a in faq_pairs]

    embeddings = model.encode(faq_texts)
    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

    return faq_pairs, faq_texts, index, embeddings

uploaded_file = st.file_uploader("📄 Upload your FAQ (.txt)", type=["txt"])

if uploaded_file:
    with open("uploaded_faq.txt", "wb") as f:
        f.write(uploaded_file.read())

    faq_pairs, faq_texts, index, embeddings = load_faq("uploaded_faq.txt")

    question = st.text_input("❓ Ask your question")

    if question:
        user_embedding = model.encode([question])
        D, I = index.search(np.array(user_embedding), k=1)
        top_idx = I[0][0]
        context = faq_texts[top_idx]

        prompt = f"""Answer the question based only on the FAQ below:

FAQ:
{context}

User Question: {question}
Answer:"""

        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant answering only from the FAQ."},
                    {"role": "user", "content": prompt}
                ]
            )
            answer = response.choices[0].message.content.strip()
            st.markdown(f"**💬 Answer:** {answer}")

else:
    st.info("Please upload a FAQ `.txt` file to start.")

