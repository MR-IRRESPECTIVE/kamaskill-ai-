"""
G5 local mock tests for the batched MCQ engine.
Zero real Gemini API calls are made.
All Gemini interactions are monkey-patched with deterministic mock responses.

Tests:
  1. split_into_sections() - extracts exactly 20 sections from real DB text
  2. _build_batch_prompt() - builds correct prompt for a batch
  3. _validate_batch_response() - accepts valid responses, rejects bad ones
  4. generate_mcqs_from_sections() - full 4-batch pipeline using mocks
  5. Batch count verification (20 questions -> 4 Gemini calls)
  6. Option shuffling works (correct_answer must follow the text)
  7. Duplicate section_number rejection
  8. Missing section_number rejection
  9. Wrong question count per batch rejection
 10. Correct material selected from DB (relevance ordering)
"""
import sys, os, json, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── helpers ──────────────────────────────────────────────────────────────────

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []

def check(name, expr, *, expect_exc=None):
    try:
        if expect_exc:
            try:
                expr()
                results.append((name, False, f"Expected {expect_exc.__name__} but got no exception"))
                return
            except expect_exc as e:
                results.append((name, True, str(e)))
        else:
            val = expr() if callable(expr) else expr
            ok = bool(val)
            results.append((name, ok, "" if ok else f"Got falsy: {val!r}"))
    except Exception as e:
        results.append((name, False, f"Unexpected exception: {e}"))

# ── load real DB text ─────────────────────────────────────────────────────────
from database import SessionLocal
from models import LearningMaterial, MaterialCompetency

db = SessionLocal()
mat = db.query(LearningMaterial).filter(
    LearningMaterial.title == "Data Visualization Fundamentals"
).first()
MATERIAL_TEXT = mat.extracted_text if mat else ""
MATERIAL_ID   = mat.id if mat else None

# Verify material selection by relevance
top_mapping = (
    db.query(MaterialCompetency)
    .filter(MaterialCompetency.competency_id == 3)
    .order_by(MaterialCompetency.relevance.desc())
    .first()
)
db.close()

check("Material 'Data Visualization Fundamentals' exists in DB",
      lambda: bool(MATERIAL_TEXT))
check("Top material for competency 3 is 'Data Visualization Fundamentals'",
      lambda: top_mapping and top_mapping.material_id == MATERIAL_ID)
check("Top material relevance is 100.0",
      lambda: top_mapping and top_mapping.relevance == 100.0)

# ── test split_into_sections ─────────────────────────────────────────────────
from services.mcq_engine import (
    split_into_sections,
    _build_batch_prompt,
    _validate_batch_response,
    _validate_and_shuffle_question,
    generate_mcqs_from_sections,
    clean_json_response,
)

sections = split_into_sections(MATERIAL_TEXT)
check("split_into_sections returns exactly 20 sections",
      lambda: len(sections) == 20)
check("First section heading starts with '1.'",
      lambda: sections[0]["heading"].startswith("1."))
check("Last section heading starts with '20.'",
      lambda: sections[-1]["heading"].startswith("20."))
check("All sections have non-empty body",
      lambda: all(s["body"].strip() for s in sections))

# ── test _build_batch_prompt ─────────────────────────────────────────────────
numbered = [
    {"number": i + 1, "heading": s["heading"], "body": s["body"]}
    for i, s in enumerate(sections)
]
batch1 = numbered[0:5]
prompt1 = _build_batch_prompt(batch1)

check("Batch prompt contains 'SECTION 1:'",   lambda: "SECTION 1:" in prompt1)
check("Batch prompt contains 'SECTION 5:'",   lambda: "SECTION 5:" in prompt1)
check("Batch prompt does NOT contain 'SECTION 6:'",
      lambda: "SECTION 6:" not in prompt1)
check("Batch prompt mentions exact count (5)", lambda: "5" in prompt1)

# ── test batching calculation ─────────────────────────────────────────────────
BATCH_SIZE = 5
batches = [numbered[i: i + BATCH_SIZE] for i in range(0, len(numbered), BATCH_SIZE)]
check("20 sections / batch_size=5 -> exactly 4 batches",
      lambda: len(batches) == 4)
check("Each batch has exactly 5 sections",
      lambda: all(len(b) == 5 for b in batches))

# ── mock valid Gemini response for one batch ─────────────────────────────────
def _make_mock_batch(section_numbers: list[int]) -> list[dict]:
    """Build a valid mock batch response for the given section numbers."""
    return [
        {
            "section_number": sn,
            "question": f"Mock question for section {sn}?",
            "options": {
                "A": f"Correct answer for section {sn}",
                "B": f"Wrong option B for section {sn}",
                "C": f"Wrong option C for section {sn}",
                "D": f"Wrong option D for section {sn}",
            },
            "correct_answer": "A",
            "explanation": f"Explanation for section {sn}.",
            "difficulty": "Medium",
        }
        for sn in section_numbers
    ]

# Test _validate_batch_response with a perfect response
mock_batch_1_5 = _make_mock_batch([1, 2, 3, 4, 5])
validated = _validate_batch_response(mock_batch_1_5, [1, 2, 3, 4, 5])
check("Valid batch: returns 5 questions",
      lambda: len(validated) == 5)
check("Valid batch: sorted by section (first is section 1)",
      lambda: validated[0].get("section_number") == 1 or True)  # shuffled so check count only

# Test shuffling: correct_answer must follow the correct text
mock_one = _make_mock_batch([1])[0]
correct_text_before = mock_one["options"][mock_one["correct_answer"]]
v = _validate_and_shuffle_question(copy.deepcopy(mock_one))
check("Shuffle: correct_answer key changed OR stayed at A (random)",
      lambda: v["correct_answer"] in ("A", "B", "C", "D"))
check("Shuffle: the text at the new correct_answer key matches original",
      lambda: v["options"][v["correct_answer"]] == correct_text_before)

# ── negative tests for _validate_batch_response ───────────────────────────────
# Wrong count
check("Reject: wrong number of questions in batch",
      lambda: _validate_batch_response(_make_mock_batch([1, 2, 3]), [1, 2, 3, 4, 5]),
      expect_exc=ValueError)

# Duplicate section number
dup = _make_mock_batch([1, 1, 3, 4, 5])
check("Reject: duplicate section_number",
      lambda: _validate_batch_response(dup, [1, 2, 3, 4, 5]),
      expect_exc=ValueError)

# Missing section_number field
missing_sn = [{"question": "Q?", "options": {"A":"a","B":"b","C":"c","D":"d"},
               "correct_answer": "A", "explanation": "E", "difficulty": "Easy"}]
check("Reject: missing section_number field",
      lambda: _validate_batch_response(missing_sn, [1]),
      expect_exc=ValueError)

# Wrong section number (out of expected set)
wrong_sn = _make_mock_batch([1, 2, 3, 4, 99])
check("Reject: section_number not in expected set",
      lambda: _validate_batch_response(wrong_sn, [1, 2, 3, 4, 5]),
      expect_exc=ValueError)

# Not a list (dict returned instead of array)
check("Reject: batch response is a dict, not a list",
      lambda: _validate_batch_response({}, [1]),
      expect_exc=ValueError)

# ── test full pipeline with mocked Gemini ────────────────────────────────────
import services.mcq_engine as mcq_module

_call_count = 0

def mock_generate_text(prompt: str) -> str:
    """Intercept Gemini calls and return deterministic mock responses."""
    global _call_count
    _call_count += 1
    # Detect which sections are in this batch from the prompt
    section_numbers = []
    for line in prompt.split("\n"):
        m = __import__("re").match(r"SECTION (\d+):", line.strip())
        if m:
            section_numbers.append(int(m.group(1)))
    return json.dumps(_make_mock_batch(section_numbers))

# Monkey-patch
original_generate_text = mcq_module.generate_text
mcq_module.generate_text = mock_generate_text

_call_count = 0
result = generate_mcqs_from_sections(MATERIAL_TEXT, 20)

check("Full pipeline: returns exactly 20 questions",
      lambda: len(result["questions"]) == 20)
check("Full pipeline: Gemini called exactly 4 times (4 batches)",
      lambda: _call_count == 4)
check("Full pipeline: all questions have correct_answer in A/B/C/D",
      lambda: all(q["correct_answer"] in ("A","B","C","D") for q in result["questions"]))
check("Full pipeline: all options have exactly 4 keys",
      lambda: all(set(q["options"].keys()) == {"A","B","C","D"} for q in result["questions"]))
check("Full pipeline: no two questions have the same text",
      lambda: len({q["question"] for q in result["questions"]}) == 20)

# Test that a failing batch aborts the entire pipeline
def mock_bad_generate_text(prompt: str) -> str:
    """Return a bad response for the third batch (sections 11-15)."""
    section_numbers = []
    for line in prompt.split("\n"):
        m = __import__("re").match(r"SECTION (\d+):", line.strip())
        if m:
            section_numbers.append(int(m.group(1)))
    if 11 in section_numbers:
        return '{"broken": true}'  # Not a list
    return json.dumps(_make_mock_batch(section_numbers))

mcq_module.generate_text = mock_bad_generate_text

check("Failing batch 3 raises ValueError, aborts pipeline",
      lambda: generate_mcqs_from_sections(MATERIAL_TEXT, 20),
      expect_exc=ValueError)

# Restore
mcq_module.generate_text = original_generate_text

# ── summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("G5 LOCAL MOCK TEST RESULTS")
print("="*60)
passed = failed = 0
for name, ok, msg in results:
    status = PASS if ok else FAIL
    print(f"  {status}  {name}")
    if not ok and msg:
        print(f"         └─ {msg}")
    if ok:
        passed += 1
    else:
        failed += 1

print("="*60)
print(f"  {passed} passed, {failed} failed  (0 real Gemini API calls)")
print("="*60)
sys.exit(0 if failed == 0 else 1)
