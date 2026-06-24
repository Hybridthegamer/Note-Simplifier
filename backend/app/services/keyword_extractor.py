"""
Keyword Extraction Service — Algorithm 3.2 (Chapter 3).

Hybrid approach combining:
  - KeyBERT (semantic cosine-similarity with sentence-BERT embeddings)
  - YAKE   (statistical co-occurrence analysis)

Optionally enriches keywords with GPT-4 definitions.
"""
import os
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


def extract_keywords(text: str, top_n: int = 15, enrich_definitions: bool = True) -> List[Dict]:
    """
    Algorithm 3.2: Hybrid keyword extraction.

    Returns list of {term, score, definition} dicts.
    """
    keybert_kws = _keybert_extract(text, top_n)
    yake_kws = _yake_extract(text, top_n)

    # STEP 3: MERGE AND DEDUPLICATE by lemma
    combined = _merge_deduplicate(keybert_kws, yake_kws, top_n)

    # STEP 4: DEFINITION ENRICHMENT (optional)
    if enrich_definitions and combined:
        combined = _enrich_definitions(text, combined)

    return combined


def _keybert_extract(text: str, top_n: int) -> List[Dict]:
    try:
        from keybert import KeyBERT
        model = KeyBERT()
        results = model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            top_n=top_n,
            use_mmr=True,
            diversity=0.5,
        )
        return [{"term": kw, "score": round(float(score), 4), "source": "keybert"} for kw, score in results]
    except Exception:
        return []


def _yake_extract(text: str, top_n: int) -> List[Dict]:
    try:
        import yake
        kw_extractor = yake.KeywordExtractor(
            lan="en",
            n=3,
            dedupLim=0.7,
            top=top_n,
            features=None,
        )
        results = kw_extractor.extract_keywords(text)
        # YAKE scores are inverted (lower = more important)
        max_score = max((s for _, s in results), default=1.0) or 1.0
        return [
            {"term": kw, "score": round(1 - (score / max_score), 4), "source": "yake"}
            for kw, score in results
        ]
    except Exception:
        return []


def _merge_deduplicate(kws1: List[Dict], kws2: List[Dict], top_n: int) -> List[Dict]:
    seen: dict[str, Dict] = {}
    for kw in kws1 + kws2:
        key = kw["term"].lower().strip()
        if key not in seen or kw["score"] > seen[key]["score"]:
            seen[key] = {"term": kw["term"], "score": kw["score"], "definition": ""}
    ranked = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]


def _enrich_definitions(context: str, keywords: List[Dict]) -> List[Dict]:
    client = _get_openai()
    terms = [kw["term"] for kw in keywords]
    terms_str = "\n".join(f"- {t}" for t in terms)

    prompt = (
        f"Given the following academic text context, provide a brief one-sentence definition "
        f"for each of the following key terms as they are used in this context. "
        f"Return ONLY a JSON object mapping each term to its definition.\n\n"
        f"Terms:\n{terms_str}\n\n"
        f"Context (excerpt):\n{context[:2000]}"
    )

    try:
        response = _get_openai().chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an academic dictionary. Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1500,
        )
        import json
        definitions = json.loads(response.choices[0].message.content)
        for kw in keywords:
            kw["definition"] = definitions.get(kw["term"], "")
    except Exception:
        pass

    return keywords
