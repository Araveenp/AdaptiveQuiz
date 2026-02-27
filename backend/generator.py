"""Question Generator Engine – rule-based NLP question generation.

Generates four question types from text chunks:
  1. MCQ (multiple choice)
  2. Fill-in-the-blank
  3. True / False
  4. Short answer

Uses NLTK for sentence tokenization, POS tagging, and named-entity-like
keyword extraction.  No heavy transformer models required.
"""

import random
import re
import os
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag

# On Vercel, NLTK data must go to /tmp (filesystem is read-only elsewhere)
if os.environ.get("VERCEL"):
    nltk.data.path.insert(0, "/tmp/nltk_data")

# Ensure required NLTK data is available (download silently on first run)
for _pkg in ("punkt", "punkt_tab", "averaged_perceptron_tagger", "averaged_perceptron_tagger_eng"):
    try:
        nltk.data.find(f"tokenizers/{_pkg}" if "punkt" in _pkg else f"taggers/{_pkg}")
    except LookupError:
        nltk.download(_pkg, quiet=True, download_dir="/tmp/nltk_data" if os.environ.get("VERCEL") else None)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _extract_keywords(sentence: str, top_n: int = 5) -> list[str]:
    """Return important nouns / proper nouns from a sentence."""
    tokens = word_tokenize(sentence)
    tagged = pos_tag(tokens)
    keywords = [
        word for word, tag in tagged
        if tag in ("NN", "NNS", "NNP", "NNPS") and len(word) > 2
    ]
    # deduplicate preserving order
    seen = set()
    unique = []
    for w in keywords:
        low = w.lower()
        if low not in seen:
            seen.add(low)
            unique.append(w)
    return unique[:top_n]


def _difficulty_from_sentence(sentence: str) -> str:
    """Heuristic difficulty based on sentence length and vocabulary."""
    words = sentence.split()
    if len(words) <= 10:
        return "easy"
    if len(words) <= 25:
        return "medium"
    return "hard"


def _generate_distractors(answer: str, keywords: list[str], n: int = 3) -> list[str]:
    """Generate plausible wrong options for MCQ from available keywords."""
    candidates = [k for k in keywords if k.lower() != answer.lower()]
    # pad with generic distractors if not enough keywords
    generic = ["None of the above", "All of the above", "Not enough information",
               "Cannot be determined", "Unknown"]
    random.shuffle(generic)
    candidates.extend(generic)
    return candidates[:n]


# ---------------------------------------------------------------------------
# generators per question type
# ---------------------------------------------------------------------------

def generate_mcq(sentence: str, all_keywords: list[str]) -> dict | None:
    """Generate one MCQ from a sentence."""
    kw = _extract_keywords(sentence)
    if not kw:
        return None
    answer = kw[0]
    blanked = sentence.replace(answer, "______", 1)
    if blanked == sentence:
        return None
    distractors = _generate_distractors(answer, all_keywords)
    options = distractors[:3] + [answer]
    random.shuffle(options)
    return {
        "question_type": "mcq",
        "question_text": f"Fill in the blank: {blanked}",
        "correct_answer": answer,
        "options": options,
        "difficulty": _difficulty_from_sentence(sentence),
        "explanation": f"The correct answer is '{answer}' as stated in the source material.",
    }


def generate_fill_blank(sentence: str) -> dict | None:
    """Generate a fill-in-the-blank question."""
    kw = _extract_keywords(sentence)
    if not kw:
        return None
    answer = kw[0]
    blanked = sentence.replace(answer, "______", 1)
    if blanked == sentence:
        return None
    return {
        "question_type": "fill_blank",
        "question_text": f"Complete the sentence: {blanked}",
        "correct_answer": answer,
        "options": [],
        "difficulty": _difficulty_from_sentence(sentence),
        "explanation": f"The missing word is '{answer}'.",
    }


def generate_true_false(sentence: str, all_keywords: list[str]) -> dict | None:
    """Generate a True/False question (randomly negate the statement)."""
    kw = _extract_keywords(sentence)
    if not kw:
        return None
    make_false = random.choice([True, False])
    if make_false and len(all_keywords) > 1:
        original = kw[0]
        replacement = random.choice([k for k in all_keywords if k.lower() != original.lower()] or [original])
        altered = sentence.replace(original, replacement, 1)
        return {
            "question_type": "true_false",
            "question_text": f"True or False: {altered}",
            "correct_answer": "False",
            "options": ["True", "False"],
            "difficulty": _difficulty_from_sentence(sentence),
            "explanation": f"The statement is false. The original text says '{original}' not '{replacement}'.",
        }
    return {
        "question_type": "true_false",
        "question_text": f"True or False: {sentence}",
        "correct_answer": "True",
        "options": ["True", "False"],
        "difficulty": _difficulty_from_sentence(sentence),
        "explanation": "The statement is true as per the source material.",
    }


def generate_short_answer(sentence: str) -> dict | None:
    """Generate a short-answer question from a sentence."""
    kw = _extract_keywords(sentence)
    if not kw:
        return None
    answer = kw[0]
    # Try to create a 'What is …?' style question
    q = f"Based on the following statement, what is the key concept?\n\"{sentence}\""
    return {
        "question_type": "short_answer",
        "question_text": q,
        "correct_answer": answer,
        "options": [],
        "difficulty": _difficulty_from_sentence(sentence),
        "explanation": f"The key concept mentioned is '{answer}'.",
    }


# ---------------------------------------------------------------------------
# main entry point
# ---------------------------------------------------------------------------

_GENERATORS = {
    "mcq": generate_mcq,
    "fill_blank": generate_fill_blank,
    "true_false": generate_true_false,
    "short_answer": generate_short_answer,
}


def generate_questions_from_text(
    text: str,
    question_types: list[str] | None = None,
    difficulty: str | None = None,
    max_questions: int = 20,
) -> list[dict]:
    """Generate questions from a block of text.

    Parameters
    ----------
    text : str
        The source material.
    question_types : list[str] | None
        Subset of ['mcq', 'fill_blank', 'true_false', 'short_answer'].
        None means all types.
    difficulty : str | None
        Filter to a specific difficulty ('easy', 'medium', 'hard').
    max_questions : int
        Cap on the number of questions returned.

    Returns
    -------
    list[dict]  – list of question dicts ready to be stored in the DB.
    """
    if question_types is None:
        question_types = list(_GENERATORS.keys())

    sentences = sent_tokenize(text)
    if not sentences:
        return []

    # collect all keywords across the text for distractor generation
    all_keywords: list[str] = []
    for s in sentences:
        all_keywords.extend(_extract_keywords(s))
    # deduplicate
    seen = set()
    unique_kw = []
    for k in all_keywords:
        if k.lower() not in seen:
            seen.add(k.lower())
            unique_kw.append(k)
    all_keywords = unique_kw

    questions: list[dict] = []
    random.shuffle(sentences)

    for sentence in sentences:
        if len(questions) >= max_questions:
            break
        sentence = sentence.strip()
        if len(sentence.split()) < 5:
            continue

        for qt in question_types:
            if len(questions) >= max_questions:
                break
            gen = _GENERATORS.get(qt)
            if not gen:
                continue
            # generators that need all_keywords
            if qt in ("mcq", "true_false"):
                q = gen(sentence, all_keywords)
            else:
                q = gen(sentence)
            if q:
                if difficulty and q["difficulty"] != difficulty:
                    continue
                questions.append(q)

    return questions
