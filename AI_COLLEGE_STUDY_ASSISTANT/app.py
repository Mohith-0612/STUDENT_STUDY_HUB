
import streamlit as st
from groq import Groq
from datetime import date, timedelta
from urllib.parse import quote_plus

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="SMART STUDY HUB",
    page_icon="🎓",
    layout="wide"
)

# ==================================================
# APPLICATION TITLE
# ==================================================

st.title("🎓 SMART STUDY HUB")

st.markdown(
    """
    Your personal AI assistant for learning,
    exam preparation, quizzes, and study planning.
    """
)

# ==================================================
# SUBJECTS
# ==================================================

SUBJECTS = [
    "ADSAA",
    "DBMS",
    "Artificial Intelligence",
    "DMGT",
    "DLCO",
    "Python Programming"
]

# ==================================================
# GROQ API CONNECTION
# ==================================================

try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)

except Exception:
    st.error(
        "Groq API key not found!\n\n"
        "Open .streamlit/secrets.toml and add:\n\n"
        'GROQ_API_KEY = "your_actual_api_key"'
    )
    st.stop()


# ==================================================
# LOAD AVAILABLE GROQ MODELS
# ==================================================

@st.cache_data(ttl=300)
def get_available_models():
    """Get model IDs available to this Groq account."""

    models = client.models.list()

    model_ids = sorted(
        [model.id for model in models.data]
    )

    return model_ids


try:
    available_models = get_available_models()

except Exception as e:
    st.error(
        "Unable to load Groq models. "
        "Check your API key and internet connection."
    )
    st.code(str(e))
    st.stop()


if not available_models:
    st.error(
        "No models were returned for your Groq account. "
        "Check the models available in Groq Console."
    )
    st.stop()


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("📚 Study Assistant")
st.sidebar.caption("Choose a feature")

feature = st.sidebar.radio(
    "Navigation",
    [
        "Explain Topic",
        "Exam Answers",
        "Practice Quiz",
        "Study Timetable"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("🤖 AI Model")

selected_model = st.sidebar.selectbox(
    "Choose an available model",
    available_models
)

st.sidebar.caption(
    "Models are loaded from your Groq account."
)

st.sidebar.divider()
st.sidebar.subheader("📖 Your Subjects")

for subject_name in SUBJECTS:
    st.sidebar.write(f"• {subject_name}")


# ==================================================
# AI RESPONSE FUNCTION
# ==================================================

def get_ai_response(
    prompt,
    system_message=None,
    temperature=0.7,
    max_tokens=2500
):
    """Generate an answer using the selected Groq model."""

    if system_message is None:
        system_message = (
            "You are a friendly and knowledgeable "
            "B.Tech college study assistant. "
            "Explain concepts in simple English. "
            "Use headings, bullet points, examples, "
            "and tables whenever useful. "
            "Make answers accurate and easy to understand."
        )

    try:
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        answer = response.choices[0].message.content

        if not answer:
            return (
                "The AI returned an empty response. "
                "Try again."
            )

        return answer

    except Exception as e:
        error_message = str(e)

        if "model_not_found" in error_message.lower():
            return (
                "⚠️ The selected model is unavailable for "
                "chat completions. Choose another model "
                "from the sidebar."
            )

        if "rate_limit" in error_message.lower():
            return (
                "⚠️ Groq rate limit reached. "
                "Please wait and try again later.\n\n"
                f"Details: {error_message}"
            )

        if "authentication" in error_message.lower():
            return (
                "⚠️ Authentication failed. "
                "Check your GROQ_API_KEY in secrets.toml."
            )

        return (
            "⚠️ Unable to generate a response.\n\n"
            f"Error details: {error_message}"
        )


# ==================================================
# YOUTUBE VIDEO LINK FUNCTION
# ==================================================

def create_youtube_search_url(subject, topic):
    """Create a YouTube search URL for a subject and topic."""

    search_query = f"{subject} {topic} tutorial"

    youtube_url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(search_query)
    )

    return youtube_url


# ==================================================
# FEATURE 1: EXPLAIN TOPIC
# ==================================================

if feature == "Explain Topic":

    st.header("📘 Explain Any Topic")

    st.write(
        "Understand difficult concepts in simple English."
    )

    subject = st.selectbox(
        "Select your subject",
        SUBJECTS,
        key="explain_subject"
    )

    topic = st.text_input(
        "Enter the topic you want to understand",
        placeholder="Example: Binary Search"
    )

    explanation_level = st.selectbox(
        "Explanation level",
        [
            "Beginner-friendly",
            "Detailed explanation",
            "Exam preparation"
        ]
    )

    if st.button(
        "✨ Explain Topic",
        type="primary",
        key="explain_button"
    ):

        if not topic.strip():
            st.warning("Please enter a topic.")

        else:
            prompt = f"""
            Subject: {subject}
            Topic: {topic}
            Explanation level: {explanation_level}

            Explain this topic clearly for a B.Tech student.

            Include:

            1. Definition
            2. Meaning in simple English
            3. Step-by-step explanation
            4. Important points
            5. A simple example
            6. Applications
            7. Advantages and disadvantages, if applicable
            8. Short summary

            Use headings and examples.
            """

            with st.spinner("Generating explanation..."):
                answer = get_ai_response(prompt)

            st.markdown(answer)

            # ------------------------------------------
            # NEW FEATURE: RELATED YOUTUBE VIDEOS
            # ------------------------------------------

            st.divider()

            st.subheader("🎥 Learn Through Videos")

            st.write(
                "Watch educational videos related to "
                "the topic you just learned."
            )

            youtube_url = create_youtube_search_url(
                subject,
                topic
            )

            st.link_button(
                "▶️ Watch Related Videos on YouTube",
                youtube_url,
                type="primary"
            )

            st.caption(
                f"Video search: {subject} - {topic}"
            )


# ==================================================
# FEATURE 2: EXAM ANSWERS
# ==================================================

elif feature == "Exam Answers":

    st.header("📝 Exam Answer Generator")

    st.write(
        "Generate structured answers for your examinations."
    )

    subject = st.selectbox(
        "Select your subject",
        SUBJECTS,
        key="exam_subject"
    )

    question = st.text_area(
        "Enter your exam question",
        placeholder="Type your question here...",
        height=130
    )

    marks = st.selectbox(
        "Select marks",
        [2, 5, 10, 15]
    )

    answer_style = st.selectbox(
        "Answer style",
        [
            "Simple and easy to remember",
            "Detailed exam answer",
            "Point-wise answer"
        ]
    )

    if st.button(
        "📝 Generate Answer",
        type="primary",
        key="exam_button"
    ):

        if not question.strip():
            st.warning("Please enter a question.")

        else:
            prompt = f"""
            Subject: {subject}

            Exam question:
            {question}

            Marks: {marks}
            Answer style: {answer_style}

            Write an exam-ready answer for a B.Tech student.

            Requirements:

            1. Start with a suitable definition.
            2. Explain the concept clearly.
            3. Use headings and numbered points.
            4. Include examples where appropriate.
            5. Include a diagram description if useful.
            6. End with a short conclusion.
            7. Match the answer length to the marks.

            Use simple, clear English.
            """

            with st.spinner("Preparing your exam answer..."):
                answer = get_ai_response(
                    prompt,
                    max_tokens=3000
                )

            st.markdown(answer)


# ==================================================
# FEATURE 3: PRACTICE QUIZ
# ==================================================

elif feature == "Practice Quiz":

    st.header("🧠 Practice Quiz")

    st.write(
        "Test your knowledge with AI-generated questions."
    )

    subject = st.selectbox(
        "Select your subject",
        SUBJECTS,
        key="quiz_subject"
    )

    topic = st.text_input(
        "Enter a topic",
        placeholder="Example: SQL Joins"
    )

    number_of_questions = st.selectbox(
        "Number of questions",
        [5, 10, 15]
    )

    difficulty = st.selectbox(
        "Difficulty level",
        ["Easy", "Medium", "Hard"]
    )

    if st.button(
        "🎯 Generate Quiz",
        type="primary",
        key="quiz_button"
    ):

        if not topic.strip():
            st.warning("Please enter a topic.")

        else:
            prompt = f"""
            Create {number_of_questions} multiple-choice
            questions for a B.Tech student.

            Subject: {subject}
            Topic: {topic}
            Difficulty: {difficulty}

            For each question:

            1. Write the question.
            2. Give four options: A, B, C, and D.
            3. Clearly identify the correct answer.
            4. Explain why the answer is correct.

            Number every question.
            Avoid duplicate questions.
            Use accurate and understandable content.
            """

            with st.spinner("Creating your quiz..."):
                quiz = get_ai_response(
                    prompt,
                    max_tokens=3500
                )

            st.session_state["generated_quiz"] = quiz
            st.session_state["quiz_topic"] = topic

    if "generated_quiz" in st.session_state:

        st.divider()

        st.subheader(
            f"Quiz: {st.session_state.get('quiz_topic', '')}"
        )

        st.markdown(
            st.session_state["generated_quiz"]
        )

        st.download_button(
            label="📥 Download Quiz",
            data=st.session_state["generated_quiz"],
            file_name="practice_quiz.txt",
            mime="text/plain"
        )


# ==================================================
# FEATURE 4: STUDY TIMETABLE
# ==================================================

elif feature == "Study Timetable":

    st.header("📅 Personalized Study Timetable")

    st.write(
        "Create a study plan based on your available time."
    )

    selected_subjects = st.multiselect(
        "Select subjects",
        SUBJECTS,
        default=SUBJECTS[:3]
    )

    hours_per_day = st.slider(
        "Available study hours per day",
        min_value=1,
        max_value=12,
        value=4
    )

    number_of_days = st.slider(
        "Study plan duration (days)",
        min_value=1,
        max_value=30,
        value=7
    )

    exam_date = st.date_input(
        "Next exam date",
        value=date.today() + timedelta(days=7),
        min_value=date.today()
    )

    study_goals = st.text_area(
        "Additional goals (optional)",
        placeholder=(
            "Example: Focus more on DBMS and "
            "practice Python programs."
        )
    )

    if st.button(
        "📅 Create Timetable",
        type="primary",
        key="timetable_button"
    ):

        if not selected_subjects:
            st.warning("Please select at least one subject.")

        else:
            prompt = f"""
            Create a practical study timetable for a B.Tech
            student.

            Subjects:
            {", ".join(selected_subjects)}

            Available study hours per day:
            {hours_per_day}

            Duration:
            {number_of_days} days

            Next exam date:
            {exam_date}

            Additional goals:
            {study_goals if study_goals.strip() else "None"}

            Requirements:

            1. Create a day-by-day timetable.
            2. Include time slots and subjects.
            3. Keep total study time within the daily limit.
            4. Include short breaks.
            5. Distribute time among selected subjects.
            6. Include revision and practice.
            7. Use a Markdown table.
            8. Keep the schedule realistic.
            """

            with st.spinner("Creating your timetable..."):
                timetable = get_ai_response(
                    prompt,
                    max_tokens=3000
                )

            st.session_state["generated_timetable"] = timetable

    if "generated_timetable" in st.session_state:

        st.divider()
        st.subheader("Your Study Plan")

        st.markdown(
            st.session_state["generated_timetable"]
        )

        st.download_button(
            label="📥 Download Timetable",
            data=st.session_state["generated_timetable"],
            file_name="study_timetable.txt",
            mime="text/plain"
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "SMART STUDY HUB | Powered by Groq | "
    "Designed for B.Tech students 🎓"
)
