
#-----------------------------------------------------------------------------
"""AWS practice exam. Run: python -m streamlit run aws_quiz_app_updated.py"""
#-----------------------------------------------------------------------------


import csv
import random
import re
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="AWS Practice Exam", page_icon="☁️", layout="wide")
BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "AWS_Quiz_Bank.csv"
DB_PATH = BASE / "aws_quiz_history.sqlite3"
LETTERS = "ABCDEF"
EXAM_SECONDS = 90 * 60


@st.cache_data

def load_questions(path, modified):
    with path.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    result = []
    for n, row in enumerate(rows):
        options = {k: (row.get(f"Option {k}") or "").strip() for k in LETTERS}
        options = {k: v for k, v in options.items() if v}
        raw = (row.get("Correct Answer(s)") or "").upper()
        correct = set(re.findall(r"[A-F]", raw)) & set(options)
        stem = (row.get("Question") or "").strip()
        if not stem or len(options) < 2 or not correct:
            continue
        result.append({"id": row.get("Question ID") or str(n + 1),
                       "question": stem, "options": options, "correct": correct,
                       "explanations": {k: (row.get(f"Explanation {k}") or "").strip()
                                        for k in options}})
    return result


def connect_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        completed_at TEXT NOT NULL,
        correct INTEGER NOT NULL,
        total INTEGER NOT NULL,
        percent REAL NOT NULL,
        duration_seconds INTEGER NOT NULL,
        timed_out INTEGER NOT NULL
    )""")
    db.commit()
    return db


def start_exam(pool, count):
    selected = random.sample(range(len(pool)), count)
    st.session_state.exam = {
        "selected": selected,
        "orders": [random.sample(list(pool[i]["options"]), len(pool[i]["options"]))
                   for i in selected],
        "started": time.time(), "submitted": False, "answers": {},
        "score": None, "timed_out": False,
    }
    # Widget keys must be unique for every new exam.
    st.session_state.exam_serial = st.session_state.get("exam_serial", 0) + 1


def read_answers(pool, exam):
    serial = st.session_state.exam_serial
    answers = {}
    for idx, q_index in enumerate(exam["selected"]):
        q = pool[q_index]
        order = exam["orders"][idx]
        if len(q["correct"]) > 1:
            answers[idx] = {letter for letter in order
                            if st.session_state.get(f"multi_{serial}_{idx}_{letter}", False)}
        else:
            chosen = st.session_state.get(f"single_{serial}_{idx}", "Not answered")
            answers[idx] = {chosen} if chosen in q["options"] else set()
    return answers


def finish_exam(pool, timed_out=False):
    exam = st.session_state.exam
    if exam["submitted"]:
        return
    answers = read_answers(pool, exam)
    score = sum(answers[i] == pool[q_index]["correct"]
                for i, q_index in enumerate(exam["selected"]))
    elapsed = min(EXAM_SECONDS, max(0, int(time.time() - exam["started"])))
    exam.update(submitted=True, answers=answers, score=score, timed_out=timed_out)
    with connect_db() as db:
        db.execute("""INSERT INTO attempts
            (completed_at, correct, total, percent, duration_seconds, timed_out)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (datetime.now().astimezone().isoformat(timespec="seconds"), score,
             len(exam["selected"]), 100 * score / len(exam["selected"]),
             elapsed, int(timed_out)))


st.title("AWS Certification Practice Exam")
if not CSV_PATH.exists():
    st.error(f"Place AWS_Quiz_Bank.csv in the same folder as {Path(__file__).name}.")
    st.stop()
questions = load_questions(CSV_PATH, CSV_PATH.stat().st_mtime_ns)
if not questions:
    st.error("No valid questions found in the CSV. Check its column headings.")
    st.stop()

st.sidebar.header("Exam settings")
count = st.sidebar.slider("Questions per exam", 1, len(questions), min(65, len(questions)))
if st.sidebar.button("Start new randomized exam", type="primary") or "exam" not in st.session_state:
    start_exam(questions, count)
    st.rerun()

exam = st.session_state.exam
st.caption(f"{len(exam['selected'])} questions • 65-minute time limit • "
           "Questions and answer choices randomized • Results after submission")

# A Streamlit fragment updates the countdown without resetting form inputs.
# When time expires it reruns the full app so that answers are submitted once.
def show_countdown():
    remaining = max(0, EXAM_SECONDS - int(time.time() - exam["started"]))
    mins, secs = divmod(remaining, 60)
    st.metric("Time remaining", f"{mins:02d}:{secs:02d}")
    if remaining == 0 and not exam["submitted"]:
        st.rerun(scope="app")

if not exam["submitted"]:
    if time.time() - exam["started"] >= EXAM_SECONDS:
        finish_exam(questions, timed_out=True)
        st.rerun()
    if hasattr(st, "fragment"):
        st.fragment(run_every="1s")(show_countdown)()
    else:
        show_countdown()
        st.info("For a live ticking countdown, update Streamlit: python -m pip install -U streamlit")

if not exam["submitted"]:
    serial = st.session_state.exam_serial
    with st.form(f"exam_form_{serial}"):
        for idx, q_index in enumerate(exam["selected"]):
            q = questions[q_index]
            order = exam["orders"][idx]
            st.markdown(f"### {idx + 1}. {q['question']}")
            if len(q["correct"]) > 1:
                st.caption("Select all that apply")
                for position, letter in enumerate(order):
                    st.checkbox(f"{LETTERS[position]}. {q['options'][letter]}",
                                key=f"multi_{serial}_{idx}_{letter}")
            else:
                labels = {letter: f"{LETTERS[position]}. {q['options'][letter]}"
                          for position, letter in enumerate(order)}
                st.radio("Select one", ["Not answered"] + order,
                         format_func=lambda x, labels=labels: labels.get(x, x),
                         key=f"single_{serial}_{idx}", label_visibility="collapsed")
            st.divider()
        pressed = st.form_submit_button("Submit Exam", type="primary")
    if pressed:
        finish_exam(questions, timed_out=time.time() - exam["started"] >= EXAM_SECONDS)
        st.rerun()
else:
    if exam["timed_out"]:
        st.warning("Time expired. Your available answers were submitted automatically.")
    total = len(exam["selected"])
    score = exam["score"]
    st.header(f"Your score: {score}/{total} ({score / total:.0%})")
    st.progress(score / total)
    st.subheader("Answer review")
    for idx, q_index in enumerate(exam["selected"]):
        q = questions[q_index]
        given = exam["answers"][idx]
        st.markdown(f"**{idx + 1}. {q['question']}**")
        if given == q["correct"]:
            st.success("Correct")
        else:
            st.error("Incorrect" if given else "Not answered")
        st.write("Your answer:", ", ".join(q["options"][x] for x in sorted(given)) or "None")
        st.write("Correct answer:", ", ".join(q["options"][x] for x in sorted(q["correct"])))
        for letter in exam["orders"][idx]:
            explanation = q["explanations"].get(letter)
            if explanation:
                with st.expander(f"Explanation: {q['options'][letter]}",
                                 expanded=letter in q["correct"]):
                    st.write(explanation)
        st.divider()

st.sidebar.divider()
st.sidebar.subheader("Saved score history")
with connect_db() as db:
    history = db.execute("""SELECT completed_at, correct, total, percent,
                           duration_seconds, timed_out FROM attempts
                           ORDER BY id DESC LIMIT 100""").fetchall()
if history:
    st.sidebar.metric("Completed exams", len(history))
    st.sidebar.metric("Most recent score", f"{history[0][3]:.0f}%")
    if st.sidebar.button("Show score history"):
        st.session_state.show_history = not st.session_state.get("show_history", False)
    if st.session_state.get("show_history", False):
        st.subheader("Exam score history (latest 100)")
        st.dataframe([{"Completed": row[0], "Score": f"{row[1]}/{row[2]}",
                       "Percent": f"{row[3]:.1f}%", "Minutes": f"{row[4]/60:.1f}",
                       "Timed out": "Yes" if row[5] else "No"} for row in history],
                     use_container_width=True, hide_index=True)
        st.download_button("Download score history (CSV)",
                           "Completed,Correct,Total,Percent,Duration seconds,Timed out\n" +
                           "\n".join(",".join(map(str, row)) for row in history),
                           file_name="aws_quiz_score_history.csv", mime="text/csv")
else:
    st.sidebar.caption("Your scores will appear here after your first submission.")
st.sidebar.caption("History is stored locally in aws_quiz_history.sqlite3 next to the app.")
