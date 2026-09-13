"""
G7 - Full API-level E2E test against the live backend at 127.0.0.1:8000
MOCK_GEMINI=true is set on the server side.
This script makes NO Gemini API calls itself.
"""
import sys, os, json, requests

BASE = "http://127.0.0.1:8000"
EMPLOYEE_ID = 1
COMPETENCY_ID = 3
NUM_QUESTIONS = 20

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
results = []

def check(name, expr_or_callable, detail=""):
    try:
        val = expr_or_callable() if callable(expr_or_callable) else expr_or_callable
        ok = bool(val)
        results.append((name, ok, "" if ok else f"Got: {val!r} {detail}"))
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))

def step(msg):
    print(f"\n  -- {msg}")

# ══════════════════════════════════════════════════════
# PHASE 1: Dashboard data
# ══════════════════════════════════════════════════════
step("Dashboard — employee data")
emp = requests.get(f"{BASE}/employees/1", timeout=5).json()
check("Employee 1 exists", lambda: emp.get("id") == 1)
check("Employee has name", lambda: bool(emp.get("name")))

step("Dashboard — competencies")
comps_r = requests.get(f"{BASE}/competencies/employee/1", timeout=5)
comps = comps_r.json() if comps_r.status_code == 200 else []
check("Competencies endpoint returns 200", lambda: comps_r.status_code == 200)
check("At least one competency returned", lambda: len(comps) > 0)

dv = next((c for c in comps if c.get("competency_id") == 3 or
           (c.get("competency") and c["competency"].get("id") == 3)), None)
# Some APIs return flat, some nested
if dv is None:
    dv = next((c for c in comps if "data" in str(c).lower() and "visual" in str(c).lower()), None)
check("Data Visualization competency present", lambda: dv is not None)
current_level_before = None
if dv:
    current_level_before = dv.get("current_level")
    required_level = dv.get("required_level")
    check("current_level is a number (not None/NaN)", lambda: isinstance(current_level_before, (int, float)))
    check("required_level is a number (not None/NaN)", lambda: isinstance(required_level, (int, float)))
    print(f"     current_level={current_level_before}  required_level={required_level}")

step("Dashboard — recommendations pre-assessment")
recs_r = requests.get(f"{BASE}/recommendations/employee/1", timeout=5)
check("Recommendations endpoint returns 200", lambda: recs_r.status_code == 200)

# ══════════════════════════════════════════════════════
# PHASE 2: Assessment Generation
# ══════════════════════════════════════════════════════
step("Assessment — POST /assessments/generate")
gen_r = requests.post(f"{BASE}/assessments/generate", json={
    "employee_id": EMPLOYEE_ID,
    "competency_id": COMPETENCY_ID,
    "number_of_questions": NUM_QUESTIONS
}, timeout=30)
gen_body = gen_r.json() if gen_r.status_code == 200 else {}
QUIZ_ID = gen_body.get("quiz_id")

check("POST /assessments/generate returns 200", lambda: gen_r.status_code == 200)
check("Response has quiz_id", lambda: QUIZ_ID is not None)
check("number_of_questions == 20", lambda: gen_body.get("number_of_questions") == NUM_QUESTIONS)
print(f"     quiz_id={QUIZ_ID}")

# ══════════════════════════════════════════════════════
# PHASE 3: Quiz retrieval + security
# ══════════════════════════════════════════════════════
step(f"Quiz — GET /quizzes/{QUIZ_ID}")
quiz_r = requests.get(f"{BASE}/quizzes/{QUIZ_ID}", timeout=5)
quiz_body = quiz_r.json() if quiz_r.status_code == 200 else {}
questions = quiz_body.get("questions", [])

check("GET /quizzes/{id} returns 200", lambda: quiz_r.status_code == 200)
check("Exactly 20 questions returned", lambda: len(questions) == NUM_QUESTIONS)

# Security contract
first_q = questions[0] if questions else {}
check("SECURITY: correct_answer NOT in response", lambda: "correct_answer" not in first_q)
check("SECURITY: explanation NOT in response",    lambda: "explanation" not in first_q)

# Question structure
check("All questions have A/B/C/D options",
      lambda: all(set(q.get("options", {}).keys()) == {"A","B","C","D"} for q in questions))
check("All question texts non-empty",
      lambda: all(q.get("question","").strip() for q in questions))
check("All option values unique per question",
      lambda: all(len(set(q.get("options",{}).values())) == 4 for q in questions))
check("All difficulty fields present",
      lambda: all(q.get("difficulty") for q in questions))

print(f"\n     Sample question 1: {questions[0]['question'][:90]}...")
print(f"     Options: A={questions[0]['options']['A'][:40]}...")

# ══════════════════════════════════════════════════════
# PHASE 4: Quiz submission — all correct
# ══════════════════════════════════════════════════════
step("Quiz — fetch correct answers from DB and submit all correct")

# Get DB correct answers (only server-side; never from the public GET)
import sys as _sys
_sys.path.insert(0, ".")
from database import SessionLocal
from models import QuizQuestion as QQ
db = SessionLocal()
db_qs = db.query(QQ).filter(QQ.quiz_id == QUIZ_ID).all()
correct_map = {q.id: q.correct_answer for q in db_qs}
db.close()

attempt_payload = {
    "employee_id": EMPLOYEE_ID,
    "answers": [
        {"question_id": qid, "answer": ans}
        for qid, ans in correct_map.items()
    ]
}
attempt_r = requests.post(f"{BASE}/quizzes/{QUIZ_ID}/attempt", json=attempt_payload, timeout=15)
attempt_body = attempt_r.json() if attempt_r.status_code == 200 else {}

check("POST /quizzes/{id}/attempt returns 200", lambda: attempt_r.status_code == 200)

result = attempt_body.get("result", {})
check("Score is 20 (all correct)", lambda: result.get("score") == NUM_QUESTIONS)
check("Percentage is 100.0",       lambda: result.get("percentage") == 100.0)
check("assessment_created is True", lambda: attempt_body.get("assessment_created") is True)
check("competency_id present in response", lambda: attempt_body.get("competency_id") is not None)

new_competency_level = attempt_body.get("new_competency_level")
check("new_competency_level present (not None)", lambda: new_competency_level is not None)
if new_competency_level is not None and current_level_before is not None:
    check("new_competency_level >= current_level_before (went up)",
          lambda: new_competency_level >= current_level_before)
    print(f"     competency: {current_level_before} -> {new_competency_level}")

print(f"\n     question_results sample: {attempt_body.get('question_results',[{}])[:2]}")

# ══════════════════════════════════════════════════════
# PHASE 5: Post-submission state
# ══════════════════════════════════════════════════════
step("Post-submission — competency updated in DB")
comps2_r = requests.get(f"{BASE}/competencies/employee/1", timeout=5)
comps2 = comps2_r.json() if comps2_r.status_code == 200 else []
dv2 = next((c for c in comps2 if c.get("competency_id") == 3 or
            "data" in str(c).lower() and "visual" in str(c).lower()), None)
if dv2:
    current_level_after = dv2.get("current_level")
    check("current_level_after is a number", lambda: isinstance(current_level_after, (int, float)))
    if current_level_before is not None:
        check("Competency level increased after full-score attempt",
              lambda: current_level_after >= current_level_before)
        print(f"     DB competency: {current_level_before} -> {current_level_after}")

step("Post-submission — recommendations still load (Learning page)")
recs2_r = requests.get(f"{BASE}/recommendations/employee/1", timeout=5)
check("Recommendations still return 200 after assessment", lambda: recs2_r.status_code == 200)
recs2 = recs2_r.json() if recs2_r.status_code == 200 else []
check("At least one recommendation present", lambda: len(recs2) > 0)

step("Post-submission — assessments history (Progress page)")
hist_r = requests.get(f"{BASE}/assessments/employee/1", timeout=5)
check("Assessment history endpoint returns 200", lambda: hist_r.status_code == 200)
hist = hist_r.json() if hist_r.status_code == 200 else []
check("At least one assessment in history", lambda: len(hist) > 0)

# ══════════════════════════════════════════════════════
# PHASE 6: Dashboard reload (return)
# ══════════════════════════════════════════════════════
step("Dashboard reload after assessment")
emp2 = requests.get(f"{BASE}/employees/1", timeout=5)
comps3_r = requests.get(f"{BASE}/competencies/employee/1", timeout=5)
check("Employee endpoint still returns 200", lambda: emp2.status_code == 200)
check("Competencies endpoint still returns 200", lambda: comps3_r.status_code == 200)

# ══════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════
print("\n" + "="*66)
print("G7 API E2E TEST RESULTS")
print("="*66)
passed = failed = 0
for name, ok, msg in results:
    if ok:
        print(f"  {GREEN}PASS{RESET}  {name}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET}  {name}")
        if msg:
            print(f"         | {msg}")
        failed += 1
print("="*66)
print(f"  {passed} passed, {failed} failed  |  quiz_id={QUIZ_ID}")
print("="*66)
sys.exit(0 if failed == 0 else 1)
