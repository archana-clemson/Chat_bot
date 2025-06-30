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
    return best_match if best_score > 0 else None

def is_greeting(text):
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    text = clean_text(text)
    return any(greet in text for greet in greetings)

def is_thanks(text):
    thanks_words = ['thanks', 'thank you', 'thx', 'thank']
    text = clean_text(text)
    return any(thank in text for thank in thanks_words)

def get_bot_response(user_input, faqs, faq_dict):
    if is_greeting(user_input):
        return "Hello! How can I assist you today?"
    if is_thanks(user_input):
        return "You're welcome! Feel free to ask more questions."

    # Try exact match (case insensitive)
    for q in faq_dict:
        if clean_text(user_input) == clean_text(q):
            return faq_dict[q]

    # Try keyword match fallback
    matched_question = keyword_match(user_input, list(faq_dict.keys()))
    if matched_question:
        return faq_dict[matched_question]

    return None  # No answer found

def main():
    st.set_page_config(page_title="📚 FlexCrew FAQ Chatbot", page_icon="🤖", layout="wide")

    st.markdown(
        """
        <style>
        .chat-container {
            max-width: 700px;
            margin: auto;
            background-color: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .user-msg {
            background-color: #0084ff;
            color: white;
            padding: 8px 15px;
            border-radius: 15px 15px 0 15px;
            width: fit-content;
            max-width: 80%;
            margin-left: auto;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .bot-msg {
            background-color: #e4e6eb;
            color: black;
            padding: 8px 15px;
            border-radius: 15px 15px 15px 0;
            width: fit-content;
            max-width: 80%;
            margin-bottom: 10px;
            font-size: 16px;
        }
        .footer {
            font-size: 14px;
            color: #666;
            text-align: center;
            margin-top: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("📚 FlexCrew FAQ Chatbot")
    st.write("Ask me anything from the FAQ!")

    if "history" not in st.session_state:
        st.session_state.history = []
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "unsatisfied_count" not in st.session_state:
        st.session_state.unsatisfied_count = 0

    faqs = load_faq()
    faq_dict = dict(faqs)

    def add_to_history(user_msg, bot_msg):
        st.session_state.history.append({"user": user_msg, "bot": bot_msg})

    # Show chat history
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.history:
            st.markdown(f"<div class='user-msg'>{chat['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='bot-msg'>{chat['bot']}</div>", unsafe_allow_html=True)

    # Input box
    user_input = st.text_input("Type your question here...", key="input")

    if user_input:
        st.session_state.question_count += 1
        bot_reply = get_bot_response(user_input, faqs, faq_dict)

        if bot_reply is None:
            bot_reply = "Sorry, I couldn't find a good answer in the FAQ."
            st.session_state.unsatisfied_count += 1
        else:
            st.session_state.unsatisfied_count = 0  # reset on answer found

        add_to_history(user_input, bot_reply)

        # Clear input box after submit
        st.experimental_rerun()

    # After 3 unanswered questions, suggest support
    if st.session_state.unsatisfied_count >= 3:
        st.warning(
            "If you're not satisfied with the answers, please contact our support team at "
            "[support@flexcrew.com](mailto:support@flexcrew.com) or call 1-800-123-4567."
        )

    st.markdown("<div class='footer'>Powered by FlexCrew FAQ Chatbot</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
