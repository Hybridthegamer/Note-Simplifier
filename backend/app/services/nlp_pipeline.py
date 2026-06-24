"""
NLP Processing Pipeline — Algorithm 3.1 (Chapter 3).

Stage 1: TF-IDF extractive pre-processing via NLTK.
Stage 2: Chunk management (max 1024 tokens per chunk).
Stage 3: Abstractive simplification via OpenAI GPT-4.
Stage 4: Post-processing and word count.
"""
import os
import re
import math
from typing import List, Tuple
from collections import Counter

import nltk
from openai import OpenAI

nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

_openai_client = None


def _get_openai():
    global _openai_client
    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client


COMPLEXITY_PROMPTS = {
    "basic": (
        "You are an academic tutor. Rewrite the following academic text for a beginner-level "
        "student who has no prior knowledge of the subject. Use very simple language, short "
        "sentences, everyday vocabulary, and clear explanations. Avoid jargon. Preserve all "
        "factual accuracy. Format with clear paragraphs."
    ),
    "intermediate": (
        "You are an academic tutor. Rewrite the following academic text for an intermediate-level "
        "student with some subject knowledge. Simplify complex sentences, explain technical terms "
        "briefly in parentheses, and maintain a clear logical flow. Preserve all factual accuracy. "
        "Format with clear paragraphs."
    ),
    "advanced": (
        "You are an academic tutor. Rewrite the following academic text for an advanced student "
        "preparing for examinations. Maintain technical terminology, condense verbose passages, "
        "and highlight key principles. Preserve all factual accuracy. Format with clear paragraphs."
    ),
}


def _compute_tfidf_scores(sentences: List[str], stop_words: set) -> dict:
    """Compute per-sentence TF-IDF importance scores."""
    n = len(sentences)
    word_doc_freq: Counter = Counter()

    tokenised = []
    for sent in sentences:
        words = [w.lower() for w in re.findall(r"\b\w+\b", sent) if w.lower() not in stop_words]
        tokenised.append(words)
        word_doc_freq.update(set(words))

    scores = {}
    for idx, words in enumerate(tokenised):
        if not words:
            scores[idx] = 0.0
            continue
        tf: Counter = Counter(words)
        score = sum(
            (tf[w] / len(words)) * math.log((n + 1) / (word_doc_freq[w] + 1))
            for w in tf
        )
        scores[idx] = score / len(words)
    return scores


def _chunk_text(sentences: List[str], max_tokens: int = 1024) -> List[str]:
    """Split sentence list into chunks within the model token limit (approx 4 chars/token)."""
    chunks, current, current_len = [], [], 0
    for sent in sentences:
        token_est = len(sent) // 4
        if current_len + token_est > max_tokens and current:
            chunks.append(" ".join(current))
            current, current_len = [], 0
        current.append(sent)
        current_len += token_est
    if current:
        chunks.append(" ".join(current))
    return chunks


def simplify_text(raw_text: str, complexity_level: str = "intermediate") -> Tuple[str, List[str]]:
    """
    Algorithm 3.1: Two-stage hybrid simplification pipeline.

    Returns (simplified_text, key_sentences).
    """
    complexity_level = complexity_level.lower()
    if complexity_level not in COMPLEXITY_PROMPTS:
        complexity_level = "intermediate"

    # STEP 1: PREPROCESSING
    stop_words = set(stopwords.words("english"))
    sentences = sent_tokenize(raw_text)
    if not sentences:
        return raw_text, []

    scores = _compute_tfidf_scores(sentences, stop_words)

    # STEP 1.5–1.6: Select top 40 % of sentences by TF-IDF score
    sorted_idx = sorted(scores, key=scores.get, reverse=True)
    top_n = max(1, int(len(sorted_idx) * 0.40))
    key_indices = set(sorted_idx[:top_n])
    key_sentences = [sentences[i] for i in sorted(key_indices)]

    # STEP 2: CHUNK MANAGEMENT
    chunk_list = _chunk_text(key_sentences, max_tokens=1024)

    # STEP 3: ABSTRACTIVE SIMPLIFICATION via GPT-4
    system_prompt = COMPLEXITY_PROMPTS[complexity_level]
    client = _get_openai()
    simplified_parts = []

    for chunk in chunk_list:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": chunk},
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        simplified_parts.append(response.choices[0].message.content.strip())

    # STEP 4: POST-PROCESSING
    simplified_text = "\n\n".join(simplified_parts)
    simplified_text = re.sub(r"\n{3,}", "\n\n", simplified_text).strip()

    return simplified_text, key_sentences
