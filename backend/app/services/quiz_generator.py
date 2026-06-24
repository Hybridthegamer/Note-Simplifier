"""
Quiz Generation Service — Algorithm 3.3 (Chapter 3).

Generates MCQs from simplified academic text using GPT-4 with structured JSON output.
"""
import os
import json
import random
from typing import List, Dict

from openai import OpenAI

_openai_client = None


def _get_openai():
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


def generate_quiz(simplified_text: str, num_questions: int = 10) -> List[Dict]:
    """
    Algorithm 3.3: GPT-4 MCQ generation with JSON schema validation.

    Returns list of validated MCQ dicts with shuffled options.
    """
    num_questions = max(5, min(20, num_questions))

    # STEP 1: PROMPT CONSTRUCTION
    quiz_prompt = (
        f"Generate exactly {num_questions} multiple-choice questions from the following "
        f"academic text. Each question MUST have:\n"
        f"  - 'question': a clear question stem (string)\n"
        f"  - 'options': an array of exactly 4 answer options (strings, labelled A–D)\n"
        f"  - 'correct_index': the 0-based index (0–3) of the correct option (integer)\n"
        f"  - 'explanation': a brief explanation of the correct answer (string)\n\n"
        f"Return ONLY a valid JSON object with a single key 'questions' containing the array.\n\n"
        f"Academic Text:\n{simplified_text[:4000]}"
    )

    # STEP 2: GPT-4 API CALL
    client = _get_openai()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert academic quiz creator. Return valid JSON only."},
            {"role": "user", "content": quiz_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
        max_tokens=3000,
    )

    raw = json.loads(response.choices[0].message.content)
    raw_questions = raw.get("questions", [])

    # STEP 3: SCHEMA VALIDATION
    validated = []
    for q in raw_questions:
        if not all(k in q for k in ("question", "options", "correct_index", "explanation")):
            continue
        if not isinstance(q["options"], list) or len(q["options"]) != 4:
            continue
        if q["correct_index"] not in [0, 1, 2, 3]:
            continue
        validated.append(q)

    # STEP 4: SHUFFLE OPTIONS (maintain correct_index mapping)
    shuffled = []
    for q in validated:
        correct_answer = q["options"][q["correct_index"]]
        options = q["options"][:]
        random.shuffle(options)
        new_correct_index = options.index(correct_answer)
        shuffled.append({
            "question": q["question"],
            "options": options,
            "correct_index": new_correct_index,
            "explanation": q["explanation"],
        })

    return shuffled
