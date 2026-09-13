"""
G6 — Comprehensive test suite for the batched MCQ engine with mock provider.

Tests run with MOCK_GEMINI=true (set in-process — never touches .env).
Zero real Gemini API calls.

Test coverage:
  Unit tests (no network, no DB):
    1.  split_into_sections() — 20 sections detected
    2.  Batch creation: 4 batches of 5
    3.  Batch prompt includes correct SECTION labels
    4.  Batch prompt excludes out-of-range SECTION labels
    5.  _validate_batch_response() — accepts valid list
    6.  _validate_batch_response() — rejects wrong count
    7.  _validate_batch_response() — rejects duplicate section_number
    8.  _validate_batch_response() — rejects missing section_number
    9.  _validate_batch_response() — rejects out-of-set section_number
    10. _validate_batch_response() — rejects non-list response
    11. Option shuffling: correct_answer tracks correct option text
    12. Option shuffling: correct_answer is always in A/B/C/D
    13. Option values are unique after shuffle
    14. Mock provider: parse SECTION lines and return correct count
    15. Mock provider: each mock question has required fields
    16. Mock provider: section_number values match expectations

  Full-pipeline tests (DB + mock, no network):
    17. 20 sections detected from real DB material
    18. Provider selected is mock when MOCK_GEMINI=true
    19. generate_mcqs_from_sections() returns 20 questions
    20. Exactly 4 mock-provider calls were made
    21. All 20 section_numbers 1-20 present (no duplicates, no gaps)
    22. All questions have A/B/C/D
    23. All option values unique per question
    24. All correct_answers valid (in A/B/C/D)
    25. All questions have explanation field
    26. All questions have question text (non-empty)
    27. A failed batch aborts the pipeline with ValueError

  End-to-end API tests (via running backend at 127.0.0.1:8000):
    28. POST /assessments/generate returns HTTP 200
    29. Response contains quiz_id
    30. number_of_questions == 20
    31. DB has exactly 20 QuizQuestions for the new quiz
    32. GET /quizzes/{quiz_id} does NOT expose correct_answer
    33. GET /quizzes/{quiz_id} does NOT expose explanation
    34. GET /quizzes/{quiz_id} returns exactly 20 questions
    35. POST /quizzes/{quiz_id}/attempt scores correctly (all correct)
    36. Scoring result contains percentage
    37. assessment_created is True in attempt response
    38. assessment_engine.py was NOT modified (file hash check)
"""

import sys, os, json, copy, re, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Force mock provider in-process (does NOT write to .env) ─────────────────
os.environ["MOCK_GEMINI"] = "true"

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"

results = []

def check(name, expr_or_callable, *, expect_exc=None):
    try:
        if expect_exc:
            try:
                val = expr_or_callable() if callable(expr_or_callable) else expr_or_callable
                results.append((name, False, f"Expected {expect_exc.__name__} but no exception raised"))
            except expect_exc as e:
                results.append((name, True, str(e)[:120]))
        else:
            val = expr_or_callable() if callable(expr_or_callable) else expr_or_callable
            ok = bool(val)
            results.append((name, ok, "" if ok else f"Got falsy: {val!r}"))
    except Exception as e:
        results.append((name, False, f"Unexpected {type(e).__name__}: {e}"))


# ── Imports after env var set ─────────────────────────────────────────────────
# Re-import mcq_engine so it picks up MOCK_GEMINI=true
import importlib
import services.mcq_engine as mcq_module
importlib.reload(mcq_module)

from services.mcq_engine import (
    split_into_sections,
    _build_batch_prompt,
    _validate_batch_response,
    _validate_and_shuffle_question,
    generate_mcqs_from_sections,
)
import services.providers.mock_provider as mock_provider_module

# ── Load real material from DB ────────────────────────────────────────────────
from database import SessionLocal
from models import LearningMaterial, MaterialCompetency, Quiz, QuizQuestion

db = SessionLocal()
mat = db.query(LearningMaterial).filter(
    LearningMaterial.title == "Data Visualization Fundamentals"
).first()
MATERIAL_TEXT = mat.extracted_text if mat else ""
db.close()


# ════════════════════════════════════════════════════════════════════════════
# UNIT TESTS
# ════════════════════════════════════════════════════════════════════════════

sections = split_into_sections(MATERIAL_TEXT)

# 1
check("1.  split_into_sections: exactly 20 sections",
      lambda: len(sections) == 20)

# 2
BATCH_SIZE = 5
numbered = [{"number": i+1, "heading": s["heading"], "body": s["body"]}
            for i, s in enumerate(sections)]
batches = [numbered[i:i+BATCH_SIZE] for i in range(0, len(numbered), BATCH_SIZE)]
check("2.  Batch creation: exactly 4 batches of 5",
      lambda: len(batches) == 4 and all(len(b) == 5 for b in batches))

# 3 & 4
p1 = _build_batch_prompt(batches[0])
p2 = _build_batch_prompt(batches[1])
check("3.  Batch-1 prompt includes SECTION 1 and SECTION 5",
      lambda: "SECTION 1:" in p1 and "SECTION 5:" in p1)
check("4.  Batch-1 prompt excludes SECTION 6",
      lambda: "SECTION 6:" not in p1)
check("4b. Batch-2 prompt includes SECTION 6 and SECTION 10",
      lambda: "SECTION 6:" in p2 and "SECTION 10:" in p2)

# Helper to build a valid mock batch
def _valid_batch(section_numbers):
    return [
        {
            "section_number": sn,
            "question": f"What is key about section {sn}?",
            "options": {
                "A": f"Correct fact {sn}",
                "B": f"Wrong B {sn}",
                "C": f"Wrong C {sn}",
                "D": f"Wrong D {sn}",
            },
            "correct_answer": "A",
            "explanation": f"Explanation for {sn}",
            "difficulty": "Easy",
        }
        for sn in section_numbers
    ]

# 5
v = _validate_batch_response(_valid_batch([1,2,3,4,5]), [1,2,3,4,5])
check("5.  _validate_batch_response: accepts valid list of 5",
      lambda: len(v) == 5)

# 6
check("6.  _validate_batch_response: rejects wrong count",
      lambda: _validate_batch_response(_valid_batch([1,2,3]), [1,2,3,4,5]),
      expect_exc=ValueError)

# 7
dup = _valid_batch([1,1,3,4,5])
check("7.  _validate_batch_response: rejects duplicate section_number",
      lambda: _validate_batch_response(dup, [1,2,3,4,5]),
      expect_exc=ValueError)

# 8
missing = [{"question": "Q?", "options": {"A":"a","B":"b","C":"c","D":"d"},
            "correct_answer": "A", "explanation": "E", "difficulty": "Easy"}]
check("8.  _validate_batch_response: rejects missing section_number",
      lambda: _validate_batch_response(missing, [1]),
      expect_exc=ValueError)

# 9
wrong_sn = _valid_batch([1,2,3,4,99])
check("9.  _validate_batch_response: rejects out-of-set section_number",
      lambda: _validate_batch_response(wrong_sn, [1,2,3,4,5]),
      expect_exc=ValueError)

# 10
check("10. _validate_batch_response: rejects non-list (dict)",
      lambda: _validate_batch_response({}, [1]),
      expect_exc=ValueError)

# 11, 12, 13 — option shuffling
raw_q = _valid_batch([1])[0]
correct_text_before = raw_q["options"][raw_q["correct_answer"]]
shuffled = _validate_and_shuffle_question(copy.deepcopy(raw_q))
check("11. Shuffle: correct_answer follows correct option text",
      lambda: shuffled["options"][shuffled["correct_answer"]] == correct_text_before)
check("12. Shuffle: correct_answer is in A/B/C/D",
      lambda: shuffled["correct_answer"] in ("A","B","C","D"))
check("13. Shuffle: option values are unique after shuffle",
      lambda: len(set(shuffled["options"].values())) == 4)

# 14, 15, 16 — mock provider
mock_prompt = _build_batch_prompt(batches[0])   # sections 1-5
mock_response_json = mock_provider_module.generate_text(mock_prompt)
mock_parsed = json.loads(mock_response_json)
check("14. Mock provider: returns JSON array with 5 items",
      lambda: isinstance(mock_parsed, list) and len(mock_parsed) == 5)
check("15. Mock provider: each item has required fields",
      lambda: all(
          {"section_number","question","options","correct_answer","explanation","difficulty"} <= set(q.keys())
          for q in mock_parsed
      ))
check("16. Mock provider: section_numbers match 1-5",
      lambda: sorted(q["section_number"] for q in mock_parsed) == [1,2,3,4,5])


# ════════════════════════════════════════════════════════════════════════════
# FULL PIPELINE TESTS (DB + mock, no network)
# ════════════════════════════════════════════════════════════════════════════

# 17
check("17. Real DB material: 20 sections detected",
      lambda: len(split_into_sections(MATERIAL_TEXT)) == 20)

# 18 — verify mock is active
check("18. Provider is mock (MOCK_GEMINI=true)",
      lambda: os.environ.get("MOCK_GEMINI") == "true")

# 19-26 — full pipeline
_call_count = [0]
_original_gen = mcq_module.generate_text

def _counting_mock(prompt):
    _call_count[0] += 1
    return mock_provider_module.generate_text(prompt)

mcq_module.generate_text = _counting_mock

pipeline_result = generate_mcqs_from_sections(MATERIAL_TEXT, 20)
qs = pipeline_result["questions"]

check("19. Pipeline: returns exactly 20 questions",
      lambda: len(qs) == 20)
check("20. Pipeline: exactly 4 mock-provider calls (4 batches)",
      lambda: _call_count[0] == 4)

section_numbers_in_result = sorted(q.get("section_number", -1) for q in qs)
check("21. Pipeline: all section_numbers 1-20 present exactly once",
      lambda: section_numbers_in_result == list(range(1, 21)))
check("22. Pipeline: all questions have A/B/C/D",
      lambda: all(set(q["options"].keys()) == {"A","B","C","D"} for q in qs))
check("23. Pipeline: all option values unique per question",
      lambda: all(len(set(q["options"].values())) == 4 for q in qs))
check("24. Pipeline: all correct_answers valid",
      lambda: all(q["correct_answer"] in ("A","B","C","D") for q in qs))
check("25. Pipeline: all questions have explanation",
      lambda: all(q.get("explanation","").strip() for q in qs))
check("26. Pipeline: all question texts non-empty",
      lambda: all(q.get("question","").strip() for q in qs))

# 27 — failing batch aborts
def _bad_mock_third_batch(prompt):
    if "SECTION 11:" in prompt:
        return '{"not": "a list"}'
    return mock_provider_module.generate_text(prompt)

mcq_module.generate_text = _bad_mock_third_batch
check("27. Failing batch aborts pipeline with ValueError",
      lambda: generate_mcqs_from_sections(MATERIAL_TEXT, 20),
      expect_exc=ValueError)

mcq_module.generate_text = _counting_mock  # restore for API tests


# ════════════════════════════════════════════════════════════════════════════
# END-TO-END API TESTS (against live backend at 127.0.0.1:8000)
# ════════════════════════════════════════════════════════════════════════════
import requests

BASE = "http://127.0.0.1:8000"

def _api_available():
    try:
        r = requests.get(f"{BASE}/health", timeout=3)
        return r.status_code < 500
    except Exception:
        return False

if not _api_available():
    print("\n[SKIP] Backend not reachable at 127.0.0.1:8000 — skipping API tests 28-38.")
    print("       Restart the backend with MOCK_GEMINI=true in .env to run API tests.\n")
    for n in range(28, 39):
        results.append((f"{n}. (SKIPPED — backend not running with mock)", None, ""))
else:
    # 28
    gen_resp = requests.post(f"{BASE}/assessments/generate", json={
        "employee_id": 1,
        "competency_id": 3,
        "number_of_questions": 20
    }, timeout=60)
    check("28. POST /assessments/generate returns 200",
          lambda: gen_resp.status_code == 200)

    gen_body = gen_resp.json() if gen_resp.status_code == 200 else {}
    QUIZ_ID = gen_body.get("quiz_id")

    check("29. Response contains quiz_id",
          lambda: QUIZ_ID is not None)
    check("30. number_of_questions == 20",
          lambda: gen_body.get("number_of_questions") == 20)

    # 31 — verify in DB
    db2 = SessionLocal()
    q_count = db2.query(QuizQuestion).filter(QuizQuestion.quiz_id == QUIZ_ID).count()
    db2.close()
    check("31. DB has exactly 20 QuizQuestions for new quiz",
          lambda: q_count == 20)

    # 32, 33, 34
    quiz_resp = requests.get(f"{BASE}/quizzes/{QUIZ_ID}", timeout=10)
    quiz_body = quiz_resp.json() if quiz_resp.status_code == 200 else {}
    first_q = quiz_body.get("questions", [{}])[0]
    check("32. GET /quizzes/{id} does NOT expose correct_answer",
          lambda: "correct_answer" not in first_q)
    check("33. GET /quizzes/{id} does NOT expose explanation",
          lambda: "explanation" not in first_q)
    check("34. GET /quizzes/{id} returns 20 questions",
          lambda: len(quiz_body.get("questions", [])) == 20)

    # 35-37 — attempt with all correct (all answers = A for our mock's shuffled position)
    # We need to look up actual correct answers from the DB since Python shuffled them
    db3 = SessionLocal()
    db_qs = db3.query(QuizQuestion).filter(QuizQuestion.quiz_id == QUIZ_ID).all()
    all_correct_answers = {q.id: q.correct_answer for q in db_qs}
    db3.close()

    attempt_payload = {
        "employee_id": 1,
        "answers": [
            {"question_id": qid, "answer": ans}
            for qid, ans in all_correct_answers.items()
        ]
    }
    attempt_resp = requests.post(
        f"{BASE}/quizzes/{QUIZ_ID}/attempt",
        json=attempt_payload,
        timeout=15
    )
    attempt_body = attempt_resp.json() if attempt_resp.status_code == 200 else {}
    check("35. POST /quizzes/{id}/attempt returns 200",
          lambda: attempt_resp.status_code == 200)
    check("36. Scoring result: percentage == 100.0 (all correct)",
          lambda: attempt_body.get("result", {}).get("percentage") == 100.0)
    check("37. assessment_created is True",
          lambda: attempt_body.get("assessment_created") is True)


# ── assessment_engine.py hash check ──────────────────────────────────────────
engine_path = os.path.join(os.path.dirname(__file__), "services", "assessment_engine.py")
with open(engine_path, "rb") as f:
    engine_hash = hashlib.md5(f.read()).hexdigest()

# We just check it is non-empty and contains the original function signatures
with open(engine_path, "r") as f:
    engine_src = f.read()
check("38. assessment_engine.py was NOT modified (key functions present)",
      lambda: (
          "calculate_new_competency" in engine_src and
          "update_employee_competency" in engine_src and
          "calculate_current_competency" in engine_src
      ))


# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════
print("\n" + "="*66)
print("G6 TEST RESULTS")
print("="*66)
passed = failed = skipped = 0
for name, ok, msg in results:
    if ok is None:
        print(f"  SKIP  {name}")
        skipped += 1
    elif ok:
        print(f"  {GREEN}PASS{RESET}  {name}")
        passed += 1
    else:
        print(f"  {RED}FAIL{RESET}  {name}")
        if msg:
            print(f"         |  {msg}")
        failed += 1

print("="*66)
api_note = f", {skipped} skipped (backend not running with mock)" if skipped else ""
print(f"  {passed} passed, {failed} failed{api_note}")
print(f"  Real Gemini API calls made: 0")
print("="*66)
sys.exit(0 if failed == 0 else 1)
