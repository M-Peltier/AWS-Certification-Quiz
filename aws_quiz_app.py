import csv
import random
import re
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="AWS Practice Quiz", page_icon="☁️", layout="wide")
st.title("AWS Certification Practice Quiz")

CSV_PATH = Path(__file__).with_name("AWS_Quiz_Bank.csv")
LETTERS = "ABCDEF"

@st.cache_data
def load_questions(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    questions = []
    for row in rows:
        options = {letter: (row.get(f"Option {letter}") or "").strip()
                   for letter in LETTERS}
        options = {letter: value for letter, value in options.items() if value}
        raw = (row.get("Correct Answer(s)") or "").upper()
        correct = set(re.findall(r"[A-F]", raw)) & set(options)
        if not row.get("Question", "").strip() or not options or not correct:
            continue
        questions.append({"id": row.get("Question ID", ""),
                          "question": row["Question"].strip(),
                          "options": options, "correct": correct,
                          "explanations": {letter: (row.get(f"Explanation {letter}") or "").strip()
                                           for letter in options}})
    return questions

if not CSV_PATH.exists():
    st.error("Place AWS_Quiz_Bank.csv in the same folder as aws_quiz_app.py")
    st.stop()

questions = load_questions(CSV_PATH)
if not questions:
    st.error("No valid questions found. Check the CSV columns and correct answer letters.")
    st.stop()

if "quiz_ids" not in st.session_state:
    st.session_state.quiz_ids = []
if "submitted" not in st.session_state:
    st.session_state.submitted = False

count = st.sidebar.slider("Questions per quiz", 1, len(questions), min(10, len(questions)))
if st.sidebar.button("Start new random quiz") or not st.session_state.quiz_ids:
    st.session_state.quiz_ids = random.sample(range(len(questions)), count)
    st.session_state.submitted = False
    st.session_state.answers = {}

selected = [questions[i] for i in st.session_state.quiz_ids]
st.caption(f"{len(selected)} questions • Answers are revealed only after submission")

with st.form("quiz_form"):
    for index, question in enumerate(selected, 1):
        st.markdown(f"### {index}. {question['question']}")
        choices = [f"{letter}. {text}" for letter, text in question["options"].items()]
        if len(question["correct"]) > 1:
            st.caption("Select all that apply")
            for letter, text in question["options"].items():
                st.checkbox(f"{letter}. {text}", key=f"q{index}_{letter}")
        else:
            st.radio("Choose one answer", ["Not answered"] + choices,
                     key=f"q{index}", label_visibility="collapsed")
        st.divider()
    submitted = st.form_submit_button("Submit Quiz", type="primary")

if submitted:
    answers = {}
    for index, question in enumerate(selected, 1):
        if len(question["correct"]) > 1:
            answers[index] = {letter for letter in question["options"]
                              if st.session_state.get(f"q{index}_{letter}", False)}
        else:
            chosen = st.session_state.get(f"q{index}", "Not answered")
            answers[index] = {chosen[0]} if chosen != "Not answered" else set()
    st.session_state.answers = answers
    st.session_state.submitted = True

if st.session_state.submitted:
    answers = st.session_state.answers
    score = sum(answers.get(i, set()) == q["correct"] for i, q in enumerate(selected, 1))
    st.header(f"Your score: {score}/{len(selected)} ({score / len(selected):.0%})")
    st.progress(score / len(selected))
    st.subheader("Answer review")
    for index, question in enumerate(selected, 1):
        correct = question["correct"]
        given = answers.get(index, set())
        st.markdown(f"**{index}. {question['question']}**")
        if given == correct:
            st.success("Correct")
        else:
            st.error("Incorrect" if given else "Not answered")
        st.write("Your answer:", ", ".join(sorted(given)) or "None")
        st.write("Correct answer:", ", ".join(
            f"{letter}. {question['options'][letter]}" for letter in sorted(correct)))
        for letter, explanation in question["explanations"].items():
            if explanation:
                with st.expander(f"Explanation for option {letter}", expanded=letter in correct):
                    st.write(explanation)
        st.divider()
