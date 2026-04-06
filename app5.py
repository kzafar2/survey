import streamlit as st
import json
import csv
import io
import os
from datetime import datetime

# ---------------- 1. VARIABLE TYPES (10 pts) ----------------
# int, str, float, bool
version_int = 1
version_str = "1.0"
version_float = 1.0
is_active = True

# tuple: Scale mapping
options_scale = (
    ("Always", 0),
    ("Often", 1),
    ("Sometimes", 2),
    ("Rarely", 3),
    ("Never", 4)
)

# range: Valid scores are 0, 1, 2, 3, 4
valid_score_range = range(0, 5)

# frozenset: Allowed file formats for download
allowed_formats = frozenset(["JSON", "CSV", "TXT"])

# dict: Psychological states with ranges and descriptions
psych_states = {
    "Mastery Level Consolidation": {
        "range": (0, 8),
        "description": "Exceptional summary habits; highly efficient knowledge retention and deep understanding."
    },
    "Highly Effective Consolidator": {
        "range": (9, 17),
        "description": "Strong and consistent summarization routines; well-prepared for exams."
    },
    "Proficient Learner": {
        "range": (18, 26),
        "description": "Good consolidation habits; mostly consistent but has slight room for optimization."
    },
    "Developing Summarizer": {
        "range": (27, 35),
        "description": "Moderate effectiveness; occasionally writes summaries but needs to keep them more structured or frequent."
    },
    "Inconsistent Consolidator": {
        "range": (36, 44),
        "description": "Rarely writes summaries; misses out on the benefits of active recall and structured revision."
    },
    "Struggling Learner": {
        "range": (45, 53),
        "description": "Low consolidation; relies too heavily on raw, unorganized notes, leading to inefficient studying."
    },
    "Ineffective Study Patterns": {
        "range": (54, 60),
        "description": "No summary writing at all; high risk of knowledge loss and severe exam-season burnout."
    }
}

# ---------------- EXTERNAL DATA LOADING (10 pts) ----------------
QUESTIONS_FILE = "questions.json"

def initialize_questions_file():
    """Creates the external questions file if it doesn't exist."""
    if not os.path.exists(QUESTIONS_FILE):
        # list: Array of questions
        default_questions = [
            "How often do you write a summary immediately after finishing a lecture?",
            "How frequently do you review your raw lecture notes to create a consolidated summary?",
            "How effective do you find summary writing for retaining complex information over time?",
            "How often do you compare or discuss your summaries with classmates to ensure accuracy?",
            "How frequently do you use your written summaries as your primary revision tool before exams?",
            "How effectively do your summaries capture the main core concepts rather than just minor details?",
            "How often do you feel confident about your knowledge of a topic right after writing a summary on it?",
            "How frequently do you update your previous summaries with new information from subsequent lectures?",
            "How often do you easily identify the most important information to include in your summary without getting stuck?",
            "How effectively does summary writing reduce your overall study time during the exam season?",
            "How frequently do you translate the lecturer's words into your own words rather than just copying?",
            "How often do you organize your summaries using clear structures (e.g., bullet points, mind maps, tables)?",
            "How effectively does the process of summarising help you identify gaps in your own understanding?",
            "How frequently do you refer back to a specific summary when you get stuck on a coursework assignment?",
            "How often do you feel a sense of completion and academic readiness after finalizing a lecture summary?"
        ]
        with open(QUESTIONS_FILE, "w") as f:
            json.dump(default_questions, f, indent=4)

def load_questions() -> list:
    """Loads questions from an external JSON file."""
    with open(QUESTIONS_FILE, "r") as f:
        return json.load(f)

# Initialize and load external file
initialize_questions_file()
loaded_questions = load_questions()

# ---------------- HELPERS & VALIDATION ----------------
def validate_name(name: str) -> bool:
    if not name: 
        return False
        
    # 1. WHILE LOOP for validation
    while "  " in name:
        name = name.replace("  ", " ")
        
    # set: Allowed characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ- '")
    
    # 2. FOR LOOP for validation
    for char in name:
        if char not in allowed_chars:
            return False
    return True

def validate_dob(dob: str) -> bool:
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_student_id(sid: str) -> bool:
    if not sid: 
        return False
        
    # 3. FOR LOOP for validation
    for char in sid:
        if not char.isdigit():
            return False
    return True

def interpret_score(score: int):
    # 4. IF, ELIF, ELSE conditional statements
    if score < 0:
        return "Error", "Score cannot be negative."
    elif score > 60:
        return "Error", "Score exceeds maximum limit."
    else:
        for state, details in psych_states.items():
            low, high = details["range"]
            if low <= score <= high:
                return state, details["description"]
        return "Unknown State", "No description available."

# ---- Generators for Downloadable Files ----
def generate_json(record: dict) -> str:
    return json.dumps(record, indent=4)

def generate_csv(record: dict) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Field", "Value"])
    for key, val in record.items():
        if key != "answers":
            writer.writerow([key, val])
    writer.writerow([])
    writer.writerow(["Question", "Selected Option", "Score"])
    for ans in record["answers"]:
        writer.writerow([ans["question"], ans["selected_option"], ans["score"]])
    return output.getvalue()

def generate_txt(record: dict) -> str:
    lines = []
    for key, val in record.items():
        if key == "answers":
            lines.append("\nAnswers:")
            for ans in val:
                lines.append(f"  - {ans['question']}: {ans['selected_option']} (Score: {ans['score']})")
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines)


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
    
    if st.button("Validate & Start Survey"):
        errors = []
        if not validate_name(name):
            errors.append("Invalid Given Name. Only letters, spaces, hyphens, and apostrophes are allowed.")
        if not validate_name(surname):
            errors.append("Invalid Surname. Only letters, spaces, hyphens, and apostrophes are allowed.")
        if not validate_dob(dob):
            errors.append("Error: Date format is incorrect. Please ensure you use the exactly YYYY-MM-DD format.")
        if not validate_student_id(sid):
            errors.append("Student ID must contain digits only.")
            
        if errors:
            for e in errors:
                st.error(e)
            st.session_state['user_valid'] = False
        else:
            st.session_state['user_valid'] = True
            st.session_state['user_info'] = {"name": name, "surname": surname, "dob": dob, "sid": sid}
            if 'survey_result' in st.session_state:
                del st.session_state['survey_result']
            st.success("Details Validated! Please proceed to the questions below.")

    if st.session_state.get('user_valid', False):
        st.markdown("---")
        st.header("📝 Questionnaire")
        
        with st.form("survey_form"):
            total_score = 0
            answers = []
            
            for idx, question_text in enumerate(loaded_questions):
                opt_labels = [opt[0] for opt in options_scale]
                choice = st.selectbox(f"Q{idx+1}. {question_text}", opt_labels, key=f"q{idx}")
                
                score = next(score for label, score in options_scale if label == choice)
                
                if score in valid_score_range:
                    total_score += score
                
                answers.append({
                    "question": question_text,
                    "selected_option": choice,
                    "score": score
                })
            
            submitted = st.form_submit_button("Submit Answers")
            
            if submitted:
                status, description = interpret_score(total_score)
                u_info = st.session_state['user_info']
                
                st.session_state['survey_result'] = {
                    "name": u_info['name'],
                    "surname": u_info['surname'],
                    "dob": u_info['dob'],
                    "student_id": u_info['sid'],
                    "total_score": total_score,
                    "result": status,
                    "description": description,
                    "version": version_str,
                    "answers": answers
                }

        if 'survey_result' in st.session_state:
            record = st.session_state['survey_result']
            
            st.markdown("---")
            st.markdown(f"## ✅ Your Result: {record['result']}")
            st.markdown(f"**Total Score:** {record['total_score']} / 60")
            st.info(f"**Interpretation:** {record['description']}")
            
            st.subheader("📥 Download Your Results")
            st.write("Choose a format to save your results:")
            
            col1, col2, col3 = st.columns(3)
            
            if "JSON" in allowed_formats:
                col1.download_button(label="Download JSON", data=generate_json(record), file_name=f"{record['student_id']}.json", mime="application/json")
            if "CSV" in allowed_formats:
                col2.download_button(label="Download CSV", data=generate_csv(record), file_name=f"{record['student_id']}.csv", mime="text/csv")
            if "TXT" in allowed_formats:
                col3.download_button(label="Download TXT", data=generate_txt(record), file_name=f"{record['student_id']}.txt", mime="text/plain")

elif menu == "Load Existing Results":
    st.header("📂 Load Results")
    uploaded_file = st.file_uploader("Upload a saved result file", type=["json", "csv", "txt"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".json"):
                data = json.load(uploaded_file)
                st.json(data)
            elif uploaded_file.name.endswith(".csv"):
                content = uploaded_file.read().decode("utf-8")
                st.text(content)
            elif uploaded_file.name.endswith(".txt"):
                content = uploaded_file.read().decode("utf-8")
                st.text(content)
            st.success("File loaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")