import streamlit as st
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="FlexCrew FAQ Chatbot")

# Initialize OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

@st.cache_data
def load_faq(filepath="faq.txt"):
    """Load FAQ questions and answers from a text file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Assuming FAQs are separated by two newlines and Q/A separated by newline
    faqs = content.strip().split("\n\n")
    questions = []
    answers = []
    for faq in faqs:
        lines = faq.strip().split("\n")
        if len(lines) >= 2:
            questions.append(lines[0].strip())
            answers.append(" ".join(lines[1:]).strip())
    return questions, answers

def embed_questions(questions, client):
    """Generate embeddings for each question using OpenAI."""
    embeddings = []
    for q in questions:
        response = client.embeddings.create(
            input=q,
            model="text-embedding-ada-002"
        )
        emb = response.data[0].embedding
        embeddings.append(emb)
    return np.array(embeddings).astype("float32")

@st.cache_data
def get_index_and_embeddings(questions):
    embeddings = embed_questions(questions, client)
    return embeddings

def get_answer(user_question, questions, answers, question_embeddings):
    """Find the closest FAQ question and return the answer."""
    # Embed user question
    response = client.embeddings.create(
        input=user_question,
        model="text-embedding-ada-002"
    )
    user_emb = np.array(response.data[0].embedding).reshape(1, -1)

    # Calculate cosine similarity with all FAQ questions
    similarities = cosine_similarity(user_emb, question_embeddings)
    best_idx = np.argmax(similarities)

    # Return best matching answer
    return answers[best_idx]

def main():
    st.title("📚 FlexCrew FAQ Chatbot")
    st.write("Ask me anything from the FAQ!")

    # Load FAQ questions and answers
    questions, answers = load_faq()

    # Compute/load embeddings for FAQ questions
    question_embeddings = get_index_and_embeddings(questions)

    # User input
    user_input = st.text_input("Your question:")

    if user_input:
        answer = get_answer(user_input, questions, answers, question_embeddings)
        st.markdown(f"**Answer:** {answer}")

if __name__ == "__main__":
    main()
