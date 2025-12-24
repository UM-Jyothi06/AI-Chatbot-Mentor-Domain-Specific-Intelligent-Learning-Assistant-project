import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)

st.set_page_config(page_title="AI Mentor Website", page_icon="🤖")

if "page" not in st.session_state:
    st.session_state.page = "home"

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "experience" not in st.session_state:
    st.session_state.experience = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

# page 1: input form
if st.session_state.page == "home":
    st.title("AI Mentor Website")
    st.subheader("Get personalized mentorship using AI")

    with st.form("mentor_form"):
        topic = st.text_input("Enter the topic")
        experience = st.selectbox(
            "Select your experience level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        submit = st.form_submit_button("Start Mentorship")

    if submit:
        if topic.strip() == "":
            st.warning("Please enter a topic")
        else:
            st.session_state.topic = topic
            st.session_state.experience = experience
            st.session_state.page = "chat"
            st.rerun()

# page 2: AI Mentor Chatpage
elif st.session_state.page == "chat":
    st.title("AI Mentor Chatbot 🤖")
    st.caption(
        f"Topic: {st.session_state.topic} | "
        f"Level: {st.session_state.experience}"
    )

    # Prompt Template
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an AI mentor. Teach the topic: {topic}. "
            "User experience level: {experience}. "
            "Explain clearly, give examples, and answer doubts step-by-step."
        ),
        ("human", "{question}")
    ])

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_question = st.chat_input("Ask your doubt here...")

    if user_question:
        st.session_state.messages.append(
            {"role": "user", "content": user_question}
        )

        with st.chat_message("assistant"):
            formatted_prompt = prompt.format_messages(
                topic=st.session_state.topic,
                experience=st.session_state.experience,
                question=user_question
            )

            response = llm.invoke(formatted_prompt)
            st.markdown(response.content)

        st.session_state.messages.append(
            {"role": "assistant", "content": response.content}
        )

    # download chat
    def chat_as_text():
        content = (
            f"AI Mentor Chat\n"
            f"Topic: {st.session_state.topic}\n"
            f"Level: {st.session_state.experience}\n\n"
        )

        for m in st.session_state.messages:
            role = "User" if m["role"] == "user" else "AI Mentor"
            content += f"{role}: {m['content']}\n\n"

        return content

    st.download_button(
        label="⬇ Download Chat (.txt)",
        data=chat_as_text(),
        file_name="ai_mentor_chat.txt",
        mime="text/plain"
    )

    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.session_state.messages = []
        st.rerun()
