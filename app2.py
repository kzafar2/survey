import streamlit as st
import json
import csv
import re
from datetime import datetime

# ---------------- DATA ----------------
version_float = 1.0

# Using a standard 0-4 scale for all questions
options_scale = [
    ("Always / Very Effective", 0),
    ("Often / Effective", 1),
    ("Sometimes / Neutral", 2),
    ("Rarely / Ineffective", 3),
    ("Never / Very Ineffective", 4)
]

questions = [
    {"q": "How often do you write a summary immediately after finishing a lecture?", "opts": options_scale},
    {"q": "How frequently do you review your raw lecture notes to create a consolidated summary?", "opts": options_scale},
    {"q": "How effective do you find summary writing for retaining complex information over time?", "opts": options_scale},
    {"q": "How often do you compare or discuss your summaries with classmates to ensure accuracy?", "opts": options_scale},
    {"q": "How frequently do you use your written summaries as your primary revision tool before exams?", "opts": options_scale},
    {"q": "How effectively do your summaries capture the main core concepts rather than just minor details?", "opts": options_scale},
    {"q": "How often do you feel confident about your knowledge of a topic right after writing a summary on it?", "opts": options_scale},
    {"q": "How frequently do you update your previous summaries with new information from subsequent lectures?", "opts": options_scale},
    {"q": "How often do you easily identify the most important information to include in your summary without getting stuck?", "opts": options_scale},
    {"q": "How effectively does summary writing reduce your overall study time during the exam season?", "opts": options_scale},
    {"q": "How frequently do you translate the lecturer's words into your own words rather than just copying?", "opts": options_scale},
    {"q": "How often do you organize your summaries using clear structures (e.g., bullet points, mind maps, tables)?", "opts": options_scale},
    {"q": "How effectively does the process of summarising help you identify gaps in your own understanding?", "opts": options_scale},
    {"q": "How frequently do you refer back to a specific summary when you get stuck on a coursework assignment?", "opts": options_scale},
    {"q": "How often do you feel a sense of completion and academic readiness after finalizing a lecture summary?", "opts": options_scale}
]

psych_states = {
    "Mastery Level Consolidation": (0, 8),
    "Highly Effective Consolidator": (9, 17),
    "Proficient Learner": (18, 26),
    "Developing Summarizer": (27, 35),
    "Inconsistent Consolidator": (36, 44),
    "Struggling Learner": (45, 53),
    "Ineffective Study Patterns": (54, 60)
}

# ---------------- HELPERS ----------------
def validate_name(name: str) -> bool:
    pattern = r"^[A-Za-z\- \']+$"
    return bool(re.match(pattern, name)) and len(name.strip()) > 0

def validate_dob(dob: str) -> bool:
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_student_id(sid: str) -> bool:
    return sid.isdigit() and len(sid.strip()) > 0

def interpret_score(score: int) -> str:
    for state, (low, high) in psych_states.items():
        if low <= score <= high:
            return state
    return "Unknown State"

def save_txt(filename: str, record: dict):
    with open(filename, 'w') as f:
        for key, val in record.items():
            if key == "answers":
                f.write("Answers:\n")
                for ans in val:
                    f.write(f"  - {ans['question']}: {ans['selected_option']} (Score: {ans['score']})\n")
            else:
                f.write(f"{key}: {val}\n")

def save_csv(filename: str, record: dict):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Field", "Value"])
        for key, val in record.items():
            if key != "answers":
                writer.writerow([key, val])
        writer.writerow([])
        writer.writerow(["Question", "Selected Option", "Score"])
        for ans in record["answers"]:
            writer.writerow([ans["question"], ans["selected_option"], ans["score"]])

def save_json(filename: str, record: dict):
    with open(filename, 'w') as f:
        json.dump(record, f, indent=4)

# ---------------- MAIN UI ----------------
st.set_page_config(page_title="Knowledge Consolidation Survey", layout="centered")
st.title("📚 Lecture Summary & Knowledge Consolidation Survey")

menu = st.sidebar.radio("Navigation Menu", ["Start New Questionnaire", "Load Existing Results"])

if menu == "Start New Questionnaire":
    st.header("📋 Enter Your Details")
    
    name = st.text_input("Given Name")
    surname = st.text_input("Surname")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    sid = st.text_input("Student ID (Digits only)")
    
    if st.button("Start Survey"):
        errors = []
        if not validate_name(name):
            errors.append("Invalid Given Name. Only letters, spaces, hyphens, and apostrophes are allowed.")
        if not validate_name(surname):
            errors.append("Invalid Surname. Only letters, spaces, hyphens, and apostrophes are allowed.")
        if not validate_dob(dob):
            errors.append("Invalid Date of Birth format. Please use YYYY-MM-DD.")
        if not validate_student_id(sid):
            errors.append("Student ID must contain digits only.")
            
        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state['user_valid'] = True
            st.session_state['user_info'] = {"name": name, "surname": surname, "dob": dob, "sid": sid}
            st.success("Details Validated! Please proceed to the questions below.")

    if st.session_state.get('user_valid', False):
        st.markdown("---")
        st.header("📝 Questionnaire")
        
        total_score = 0
        answers = []
        
        with st.form("survey_form"):
            for idx, q in enumerate(questions):
                opt_labels = [opt[0] for opt in q["opts"]]
                choice = st.selectbox(f"Q{idx+1}. {q['q']}", opt_labels, key=f"q{idx}")
                
                score = next(score for label, score in q["opts"] if label == choice)
                total_score += score
                
                answers.append({
                    "question": q["q"],
                    "selected_option": choice,
                    "score": score
                })
            
            save_format = st.selectbox("Choose format to save results:", ["JSON", "CSV", "TXT"])
            submitted = st.form_submit_button("Submit Answers")
            
            if submitted:
                status = interpret_score(total_score)
                u_info = st.session_state['user_info']
                
                record = {
                    "name": u_info['name'],
                    "surname": u_info['surname'],
                    "dob": u_info['dob'],
                    "student_id": u_info['sid'],
                    "total_score": total_score,
                    "result": status,
                    "version": version_float,
                    "answers": answers
                }
                
                st.markdown(f"## ✅ Your Result: {status}")
                st.markdown(f"**Total Score:** {total_score} / 60")
                
                file_ext = save_format.lower()
                filename = f"{u_info['sid']}_summary_results.{file_ext}"
                
                if file_ext == "json":
                    save_json(filename, record)
                elif file_ext == "csv":
                    save_csv(filename, record)
                elif file_ext == "txt":
                    save_txt(filename, record)
                    
                st.success(f"Results successfully saved locally as: `{filename}`")

elif menu == "Load Existing Results":
    st.header("📂 Load Results")
    uploaded_file = st.file_uploader("Upload a saved result file (JSON, CSV, or TXT)", type=["json", "csv", "txt"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".json"):
                data = json.load(uploaded_file)
                st.write(data)
            elif uploaded_file.name.endswith(".csv"):
                content = uploaded_file.read().decode("utf-8")
                st.text(content)
            elif uploaded_file.name.endswith(".txt"):
                content = uploaded_file.read().decode("utf-8")
                st.text(content)
            st.success("File loaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")