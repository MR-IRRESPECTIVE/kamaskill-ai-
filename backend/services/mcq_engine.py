import json
import re
import random
import os

from dotenv import load_dotenv

load_dotenv()

# Provider selection — reads MOCK_GEMINI from env at import time.
# Default is false; only 'true' enables the mock.
_mock_flag = os.getenv("MOCK_GEMINI", "false").strip().lower()
if _mock_flag == "true":
    from services.providers.mock_provider import generate_text
else:
    from services.providers.gemini_provider import generate_text  # type: ignore[assignment]


def clean_json_response(text: str) -> str:
    """Remove markdown code fences if Gemini wraps JSON in ```json ... ```."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def split_into_sections(extracted_text: str) -> list[dict]:
    """
    Deterministically split material text into numbered sections.

    Expects headings of the form:
        1. Section Title\nContent...
        2. Next Section\nContent...

    Returns a list of dicts: [{"heading": "1. Foo", "body": "Content..."}, ...]
    """
    # Match section starts: a line that is just a number, period, space, then text.
    # Works on both \n and Windows \r\n line endings.
    pattern = re.compile(r"(?:^|\n)(\d+\.\s+[^\n]+)", re.MULTILINE)

    matches = list(pattern.finditer(extracted_text))

    if len(matches) == 0:
        return []

    sections = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(extracted_text)
        body = extracted_text[start:end].strip()
        # Only keep sections with actual content
        if body:
            sections.append({"heading": heading, "body": body})

    return sections


def _validate_and_shuffle_question(q: dict) -> dict:
    """Validate a single raw question dict and shuffle its option positions."""
    if not all(k in q for k in ("question", "options", "correct_answer")):
        raise ValueError("Question missing required fields (question/options/correct_answer)")

    if not isinstance(q["question"], str) or not q["question"].strip():
        raise ValueError("Question text is empty")

    opts = q["options"]
    if not isinstance(opts, dict) or set(opts.keys()) != {"A", "B", "C", "D"}:
        raise ValueError("Options must have exactly keys A, B, C, D")

    if not all(isinstance(v, str) and v.strip() for v in opts.values()):
        raise ValueError("Option values must be non-empty strings")

    if len(set(opts.values())) != 4:
        raise ValueError("Option values must be unique")

    if q["correct_answer"] not in opts:
        raise ValueError("correct_answer must be one of A, B, C, D")

    # Python-side shuffle - decouple correctness from LLM answer position
    correct_text = opts[q["correct_answer"]]
    values = list(opts.values())
    random.shuffle(values)
    new_opts = {"A": values[0], "B": values[1], "C": values[2], "D": values[3]}
    q["options"] = new_opts

    for k, v in new_opts.items():
        if v == correct_text:
            q["correct_answer"] = k
            break

    return q


def _build_batch_prompt(sections_batch: list[dict]) -> str:
    """
    Build a Gemini prompt that receives multiple sections and must return
    exactly one MCQ per section, keyed by section_number.
    """
    section_count = len(sections_batch)
    section_text = ""
    for s in sections_batch:
        section_text += f"\n---\nSECTION {s['number']}: {s['heading']}\n{s['body']}\n"

    return f"""You are an expert assessment designer for India's government capacity-building ecosystem.

Below are {section_count} learning modules. Generate EXACTLY ONE multiple-choice question for EACH module.

{section_text}
---

STRICT RULES:
1. You MUST produce exactly {section_count} questions — one per section, in order.
2. Each question must be grounded ONLY in its assigned section text. Do not use outside knowledge.
3. Do not invent unsupported facts.
4. Each question must have EXACTLY 4 distinct options (A, B, C, D).
5. Exactly one correct answer per question.
6. Use varied cognitive formats across the batch: concept/definition, application, scenario, interpretation, comparison, evaluation, decision-making.
7. Include a brief explanation for each correct answer.
8. Return ONLY valid JSON. No markdown. No ```json.

Return exactly this structure — an array with exactly {section_count} objects:
[
  {{
    "section_number": <integer matching the SECTION number above>,
    "question": "Question text",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "correct_answer": "A",
    "explanation": "Short explanation",
    "difficulty": "Easy"
  }}
]"""


def _validate_batch_response(
    raw_list: list,
    expected_section_numbers: list[int]
) -> list[dict]:
    """
    Validate a parsed batch response list.
    - Exactly one entry per expected section_number.
    - No duplicates.
    - Each question passes field/option validation.
    Returns validated+shuffled list sorted by section_number.
    """
    if not isinstance(raw_list, list):
        raise ValueError(
            f"Batch response must be a JSON array, got {type(raw_list).__name__}"
        )

    if len(raw_list) != len(expected_section_numbers):
        raise ValueError(
            f"Expected {len(expected_section_numbers)} questions in batch, "
            f"got {len(raw_list)}"
        )

    seen_sections = set()
    for item in raw_list:
        sn = item.get("section_number")
        if sn is None:
            raise ValueError("A question is missing the 'section_number' field")
        if not isinstance(sn, int):
            raise ValueError(
                f"section_number must be an integer, got {type(sn).__name__}: {sn!r}"
            )
        if sn not in expected_section_numbers:
            raise ValueError(
                f"section_number {sn} is not in the expected set "
                f"{expected_section_numbers}"
            )
        if sn in seen_sections:
            raise ValueError(f"Duplicate section_number {sn} in batch response")
        seen_sections.add(sn)

    # Validate and shuffle each question; sort back into section order
    validated = []
    for item in sorted(raw_list, key=lambda x: x["section_number"]):
        validated.append(_validate_and_shuffle_question(item))

    return validated


def _generate_batch(sections_batch: list[dict]) -> list[dict]:
    """
    Send one Gemini call for a batch of sections.
    Returns a validated, shuffled list of question dicts in section order.
    """
    expected_numbers = [s["number"] for s in sections_batch]
    prompt = _build_batch_prompt(sections_batch)

    response = generate_text(prompt)
    cleaned = clean_json_response(response)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Batch for sections {expected_numbers}: Gemini returned invalid JSON — {exc}"
        )

    return _validate_batch_response(parsed, expected_numbers)


def generate_mcqs_from_sections(extracted_text: str, number_of_questions: int) -> dict:
    """
    Deterministically generate exactly one MCQ per curriculum section using
    batched Gemini calls (batch_size=5, so 20 questions → 4 API calls).

    1. Split extracted_text into numbered sections.
    2. Validate section count == number_of_questions.
    3. Chunk sections into batches of BATCH_SIZE.
    4. Call Gemini once per batch.
    5. Validate every batch.
    6. Concatenate in section order and return {"questions": [...]}.
    """
    BATCH_SIZE = 5

    sections = split_into_sections(extracted_text)

    if len(sections) != number_of_questions:
        raise ValueError(
            f"Expected {number_of_questions} curriculum sections but found "
            f"{len(sections)}. Check the learning material structure."
        )

    # Attach ordinal section numbers
    numbered = [
        {"number": i + 1, "heading": s["heading"], "body": s["body"]}
        for i, s in enumerate(sections)
    ]

    # Chunk into batches
    batches = [
        numbered[i: i + BATCH_SIZE]
        for i in range(0, len(numbered), BATCH_SIZE)
    ]

    all_questions: list[dict] = []
    for batch_idx, batch in enumerate(batches, start=1):
        batch_range = f"{batch[0]['number']}–{batch[-1]['number']}"
        try:
            questions = _generate_batch(batch)
        except ValueError as exc:
            raise ValueError(
                f"Batch {batch_idx} (sections {batch_range}) failed: {exc}"
            )
        all_questions.extend(questions)

    # Final sanity check
    if len(all_questions) != number_of_questions:
        raise ValueError(
            f"Expected {number_of_questions} questions after all batches, "
            f"got {len(all_questions)}"
        )

    return {"questions": all_questions}


# ------------------------------------------------------------------ #
# Legacy entry point kept for backward-compatibility with other callers
# ------------------------------------------------------------------ #
def generate_mcqs(material_text: str, number_of_questions: int = 5) -> dict:
    """
    Wrapper that attempts deterministic section-based generation first.
    Falls through to a warning if sections cannot be detected.
    """
    sections = split_into_sections(material_text)
    if len(sections) == number_of_questions:
        return generate_mcqs_from_sections(material_text, number_of_questions)

    # Fallback: single-shot generation (legacy behaviour for non-sectioned materials)
    prompt = f"""You are an expert assessment designer for India's government capacity-building ecosystem.

Analyze the learning material below and generate exactly {number_of_questions} high-quality multiple choice questions.

IMPORTANT RULES:
1. Questions must be based ONLY on the provided material. Do not use outside facts.
2. Distribute questions evenly across all parts of the material. Do not repeat the same fact.
3. Use a balanced mixture of: concept/definition, application, scenario, interpretation, comparison, evaluation, decision-making.
4. Each question must have exactly 4 distinct options.
5. There must be exactly one correct answer.
6. Include a short explanation for the correct answer.
7. Return ONLY valid JSON — no markdown, no ```json.

Return exactly this structure:
{{
    "questions": [
        {{
            "question": "Question text",
            "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
            "correct_answer": "A",
            "explanation": "...",
            "difficulty": "Medium"
        }}
    ]
}}

LEARNING MATERIAL:
{material_text}
"""
    response = generate_text(prompt)
    cleaned = clean_json_response(response)

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError("Gemini returned an invalid JSON response")

    if "questions" not in result or not isinstance(result["questions"], list):
        raise ValueError("Gemini response does not contain a list of questions")

    if len(result["questions"]) != number_of_questions:
        raise ValueError(
            f"Expected {number_of_questions} questions, got {len(result['questions'])}"
        )

    for q in result["questions"]:
        _validate_and_shuffle_question(q)

    return result