import streamlit as st

# Load FAQ from file
def load_faq(filename="faq.txt"):
    faqs = []
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if "|" in line:
            question, answer = line.strip().split("|", 1)
            faqs.append((question.strip().lower(), answer.strip()))
    return faqs

# Simple keyword matching for FAQ
def get_bot_response(user_input, faqs):
    user_lower = user_input.lower()
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon"]
    thanks = ["thanks", "thank you", "thx"]

    # Basic greetings
    if any(g in user_lower for g in greetings):
        return "Hello! How can I help you today?"

    # Basic thanks
    if any(t in user_lower for t in thanks):
        return "You're welcome! Let me know if you have any other questions."

    # Try to find FAQ answer by keyword matching
    for q, a in faqs:
        if all(word in user_lower for word in q.split()):
            return a

    # No good match found
    return None

# Add message to chat history
def add_to_history(user_msg, bot_msg):
    st.session_state.chat_history.append(("user", user_msg))
    st.session_state.chat_history.append(("bot", bot_msg))

def main():
    st.set_page_config(page_title="📚 FlexCrew FAQ Chatbot", page_icon="📚")

    st.title("📚 FlexCrew FAQ Chatbot")
    st.write("Ask me anything from the FAQ!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "unsatisfied_count" not in st.session_state:
        st.session_state.unsatisfied_count = 0

    faqs = load_faq()

    # Display chat messages
    for sender, msg in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f"<div style='text-align: right; background-color: #daf1da; padding:8px; border-radius:8px; margin:8px 0;'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: left; background-color: #f0f0f0; padding:8px; border-radius:8px; margin:8px 0;'>{msg}</div>", unsafe_allow_html=True)

    # User input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:", "")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_input.strip():
        st.session_state.question_count += 1
        response = get_bot_response(user_input.strip(), faqs)

        if response is None:
            response = "Sorry, I couldn't find a good answer in the FAQ."
            st.session_state.unsatisfied_count += 1
        else:
            st.session_state.unsatisfied_count = 0

        add_to_history(user_input.strip(), response)

        # After 3 unsatisfied answers, suggest callback
        if st.session_state.unsatisfied_count >= 3:
            add_to_history("bot", "It seems I couldn't help you well. Would you like us to call you for assistance?")

        # Rerun to show new messages
        st.experimental_rerun()

if __name__ == "__main__":
    main()
