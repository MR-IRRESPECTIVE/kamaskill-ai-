"""
services/providers/mock_provider.py

DEVELOPMENT-ONLY mock text-generation provider.

This provider is NEVER used unless MOCK_GEMINI=true is explicitly set in the
environment.  It produces deterministic, structured JSON responses that
satisfy the exact same JSON contract expected by mcq_engine.py — one MCQ
per section, with section_number, question, options A-D, correct_answer,
explanation, and difficulty.

Mock questions are derived from the section heading and body content so that
every question is distinct and maps unambiguously to its source section.

This file must NOT contact the Gemini API under any circumstances.
"""
import json
import re


def generate_text(prompt: str) -> str:
    """
    Parse the incoming batch prompt to extract section numbers and headings,
    then return a deterministic JSON array of MCQs — one per section.

    The prompt format emitted by _build_batch_prompt() is:
        SECTION <n>: <heading>
        <body>
    """
    # Extract all (section_number, heading) pairs from the prompt
    section_pattern = re.compile(
        r"SECTION\s+(\d+):\s+(.+?)(?=\n---|\nSECTION|\Z)", re.DOTALL
    )
    matches = section_pattern.findall(prompt)

    questions = []
    for raw_num, raw_block in matches:
        number = int(raw_num)
        # First line of raw_block is the heading; the rest is body text
        lines = raw_block.strip().splitlines()
        heading = lines[0].strip()
        body_lines = lines[1:] if len(lines) > 1 else []
        # Use first sentence of body as source material hint
        body_preview = " ".join(body_lines[:2]).strip()
        first_sentence = body_preview.split(".")[0].strip() if body_preview else heading

        # Build four plausible-looking options derived from section text
        correct_text = (
            f"[Section {number}] {first_sentence[:80]}."
            if first_sentence
            else f"The correct fact from section {number}: {heading}."
        )

        wrong_options = [
            f"[Distractor A{number}] An incorrect claim not stated in section {number}.",
            f"[Distractor B{number}] A plausible but unsupported statement about {heading}.",
            f"[Distractor C{number}] A misattribution from a different section of the material.",
        ]

        questions.append({
            "section_number": number,
            "question": (
                f"[Section {number} — {heading}] "
                f"According to the learning material, which of the following "
                f"best describes a key point about '{heading}'?"
            ),
            "options": {
                "A": correct_text,
                "B": wrong_options[0],
                "C": wrong_options[1],
                "D": wrong_options[2],
            },
            "correct_answer": "A",
            "explanation": (
                f"Option A correctly reflects the material in section {number} "
                f"({heading}). The other options are fabricated distractors."
            ),
            "difficulty": "Easy",
        })

    return json.dumps(questions)
