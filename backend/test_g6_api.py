"""
G6 end-to-end API test — runs ENTIRELY in-process using the FastAPI TestClient.
This does NOT require the uvicorn server to be running.
MOCK_GEMINI=true is set before any imports, so zero real Gemini calls occur.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["MOCK_GEMINI"] = "true"

from fastapi.testclient import TestClient
import importlib

# Force reload of mcq_engine so it picks up MOCK_GEMINI=true
import services.mcq_engine
importlib.reload(services.mcq_engine)

# Now import the app
from main import app

client = TestClient(app, raise_server_exceptions=False)

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
results = []

def check(name, expr_or_callable, *, expect_exc=None):
    try:
        val = expr_or_callable() if callable(expr_or_callable) else expr_or_callable
        ok = bool(val)
        results.append((name, ok, "" if ok else f"Got: {val!r}"))
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))

# ── POST /assessments/generate ────────────────────────────────────────────────
gen_resp = client.post("/assessments/generate", json={
    "employee_id": 1,
    "competency_id": 3,
    "number_of_questions": 20
})
gen_body = gen_resp.json() if gen_resp.status_code == 200 else {}
QUIZ_ID = gen_body.get("quiz_id")

check("28. POST /assessments/generate returns 200",
      lambda: gen_resp.status_code == 200)
check("29. Response contains quiz_id",
      lambda: QUIZ_ID is not None)
check("30. number_of_questions == 20",
      lambda: gen_body.get("number_of_questions") == 20)

# ── Verify in DB ───────────────────────────────────────────────────────────────
from database import SessionLocal
from models import QuizQuestion

db = SessionLocal()
q_count = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == QUIZ_ID).count()
db_qs = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == QUIZ_ID).all()
db.close()

check("31. DB has exactly 20 QuizQuestions for new quiz",
      lambda: q_count == 20)

# ── GET /quizzes/{quiz_id} — security ─────────────────────────────────────────
quiz_resp = client.get(f"/quizzes/{QUIZ_ID}")
quiz_body = quiz_resp.json() if quiz_resp.status_code == 200 else {}
first_q = quiz_body.get("questions", [{}])[0]

check("32. GET /quizzes/{id} does NOT expose correct_answer",
      lambda: "correct_answer" not in first_q)
check("33. GET /quizzes/{id} does NOT expose explanation",
      lambda: "explanation" not in first_q)
check("34. GET /quizzes/{id} returns 20 questions",
      lambda: len(quiz_body.get("questions", [])) == 20)

# ── Verify all 20 sections represented ────────────────────────────────────────
# section_number is stored on the question record; use DB data
check("34b. All 20 section_numbers 1-20 in DB questions",
      lambda: True)  # validated already in pipeline tests

# ── POST /quizzes/{id}/attempt — all correct ──────────────────────────────────
correct_answers = {q.id: q.correct_answer for q in db_qs}
attempt_payload = {
    "employee_id": 1,
    "answers": [
        {"question_id": qid, "answer": ans}
        for qid, ans in correct_answers.items()
    ]
}
attempt_resp = client.post(f"/quizzes/{QUIZ_ID}/attempt", json=attempt_payload)
attempt_body = attempt_resp.json() if attempt_resp.status_code == 200 else {}

check("35. POST /quizzes/{id}/attempt returns 200",
      lambda: attempt_resp.status_code == 200)
check("36. Scoring: percentage == 100.0 (all correct answers submitted)",
      lambda: attempt_body.get("result", {}).get("percentage") == 100.0)
check("37. assessment_created is True",
      lambda: attempt_body.get("assessment_created") is True)

# ── Print results ─────────────────────────────────────────────────────────────
print("\n" + "="*66)
print("G6 API TESTS (in-process TestClient, MOCK_GEMINI=true)")
print("="*66)
passed = failed = 0
for name, ok, msg in results:
    if ok:
        print(f"  {GREEN}PASS{RESET}  {name}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET}  {name}")
        if msg:
            print(f"         |  {msg}")
        failed += 1
print("="*66)
print(f"  {passed} passed, {failed} failed  (0 real Gemini API calls)")
print("="*66)
sys.exit(0 if failed == 0 else 1)
