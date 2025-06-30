import streamlit as st
import re

def load_faq(filename="faq.txt"):
    faqs = []
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
    blocks = content.split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        question = None
        answer = None
        for line in lines:
            if line.startswith("Q:"):
                question = line[2:].strip()
            elif line.startswith("A:"):
                answer = line[2:].strip()
        if question and answer:
            faqs.append((question, answer))
    return faqs

def clean_text(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower())

def keyword_match(user_question, faq_questions):
    user_words = set(clean_text(user_question).split())
    best_match = None
    best_score = 0
    for q in faq_questions:
        faq_words = set(clean_text(q).split())
        common_words = user_words.intersection(faq_words)
        score = len(common_words)
        if score > best_score:
            best_score = score
            best_match = q
    return best_match

def is_greeting(text):
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    text = clean_text(text)
    return any(greet in text for greet in greetings)

def is_thanks(text):
    thanks_words = ['thanks', 'thank you', 'thx', 'thank']
    text = clean_text(text)
    return any(thank in text for thank in thanks_words)

def main():
    st.title("📚 FlexCrew Support")
    st.write("Ask me anything from the FAQ!")

    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = ""

    faqs = load_faq()
    questions = [q for q, a in faqs]

    user_input = st.text_input("Your question:")

    if user_input:
        st.session_state.question_count += 1

        if is_greeting(user_input):
            st.write("Hello! How can I assist you today?")
            st.session_state.last_answer = "greeting"
        elif is_thanks(user_input):
            st.write("You're welcome! Let me know if you have more questions.")
            st.session_state.last_answer = "thanks"
        else:
            match = keyword_match(user_input, questions)
            if match:
                answer = dict(faqs)[match]
                st.markdown(f"**Q:** {match}")
                st.markdown(f"**A:** {answer}")
                st.session_state.last_answer = answer
            else:
                st.write("Sorry, I couldn't find a good answer in the FAQ.")
                st.session_state.last_answer = "no_answer"

        # After 3 questions, if last answer was no_answer, ask if user wants to contact support
        if st.session_state.question_count >= 3 and st.session_state.last_answer == "no_answer":
            st.warning("If you're not satisfied with the answers, please contact our support team at support@flexcrew.com or call 1-800-123-4567.")

if __name__ == "__main__":
    main()
