"""
rag_engine.py
─────────────────────────────────────────────────────────────────────────────
Retrieval-Augmented Generation engine for the NLP-Medora chatbot.

Pipeline:
  1. INDEX   -> builds/loads a TF-IDF index over the medical Q&A corpus
               (data/fine_tune_data.jsonl) + disease_info.json + intents.json.
  2. RETRIEVE-> given a user query, finds the top-k most relevant knowledge
               chunks via cosine similarity over TF-IDF vectors.
  3. PREDICT -> extracts known symptom phrases from the query and, if any are
               found, runs the existing trained RandomForest disease model
               (model/disease_rf_model.pkl) to get a probable condition.
  4. GENERATE-> builds a grounded prompt (retrieved context + prediction +
               chat history) and sends it to a locally running Ollama model.
               Falls back to a plain "here's what I found" answer built
               directly from the retrieved text if Ollama isn't reachable.

Nothing here requires new pip installs: only pandas / scikit-learn / joblib /
requests, all of which are already in requirements.txt. Ollama itself runs
as a separate local process (not a Python package) — see OLLAMA_HOST below.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Dict, Optional

import joblib
import numpy as np
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────────────────────────────────────
#  Paths & configuration
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "model")
INDEX_DIR = os.path.join(MODEL_DIR, "rag_index")

FINE_TUNE_PATH = os.path.join(DATA_DIR, "fine_tune_data.jsonl")
DISEASE_INFO_PATH = os.path.join(MODEL_DIR, "disease_info.json")
INTENTS_PATH = os.path.join(DATA_DIR, "intents.json")

RF_MODEL_PATH = os.path.join(MODEL_DIR, "disease_rf_model.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")
MODEL_METADATA_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

VECTORIZER_PATH = os.path.join(INDEX_DIR, "vectorizer.pkl")
MATRIX_PATH = os.path.join(INDEX_DIR, "tfidf_matrix.pkl")
DOCS_PATH = os.path.join(INDEX_DIR, "documents.pkl")

# Ollama connection — override with env vars if it runs elsewhere / different model.
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = 60  # seconds

MAX_CONTEXT_CHARS_PER_DOC = 700  # truncate long completions when feeding the LLM
TOP_K_DEFAULT = 4


# ─────────────────────────────────────────────────────────────────────────────
#  Data classes
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class RetrievedDoc:
    question: str
    answer: str
    source: str
    score: float


@dataclass
class DiseasePrediction:
    disease: str
    confidence: float
    matched_symptoms: List[str]
    alternatives: List[Dict] = field(default_factory=list)
    info: Optional[Dict] = None


@dataclass
class RagResult:
    answer: str
    sources: List[RetrievedDoc]
    disease_prediction: Optional[DiseasePrediction]
    used_llm: bool
    llm_error: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
#  1. Knowledge base loading
# ─────────────────────────────────────────────────────────────────────────────
def _load_fine_tune_corpus() -> List[Dict]:
    docs = []
    if not os.path.exists(FINE_TUNE_PATH):
        return docs
    with open(FINE_TUNE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            q = (row.get("prompt") or "").strip()
            a = (row.get("completion") or "").strip()
            if q and a:
                docs.append({"question": q, "answer": a, "source": "medical_qa"})
    return docs


def _load_disease_info_corpus() -> List[Dict]:
    docs = []
    if not os.path.exists(DISEASE_INFO_PATH):
        return docs
    with open(DISEASE_INFO_PATH, "r", encoding="utf-8") as f:
        info = json.load(f)
    for disease, details in info.items():
        q = f"What should I know about {disease}?"
        a = (
            f"{disease} — Urgency: {details.get('urgency', 'Unknown')}. "
            f"Advice: {details.get('advice', 'Consult a doctor.')}"
        )
        docs.append({"question": q, "answer": a, "source": f"disease_info::{disease}"})
    return docs


def _load_intents_corpus() -> List[Dict]:
    docs = []
    if not os.path.exists(INTENTS_PATH):
        return docs
    with open(INTENTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for intent in data.get("intents", []):
        tag = intent.get("tag", "chitchat")
        responses = intent.get("responses", [])
        answer = " ".join(responses) if responses else ""
        for pattern in intent.get("patterns", []):
            if pattern and answer:
                docs.append({"question": pattern, "answer": answer, "source": f"intents::{tag}"})
    return docs


def build_corpus() -> List[Dict]:
    """Combine all knowledge sources into one flat list of {question, answer, source}."""
    corpus = []
    corpus.extend(_load_intents_corpus())
    corpus.extend(_load_disease_info_corpus())
    corpus.extend(_load_fine_tune_corpus())
    return corpus


# ─────────────────────────────────────────────────────────────────────────────
#  2. TF-IDF index build / load (cached to disk so it's built only once)
# ─────────────────────────────────────────────────────────────────────────────
def _index_is_stale() -> bool:
    if not (os.path.exists(VECTORIZER_PATH) and os.path.exists(MATRIX_PATH) and os.path.exists(DOCS_PATH)):
        return True
    try:
        index_mtime = os.path.getmtime(DOCS_PATH)
        source_mtime = max(
            os.path.getmtime(p) for p in (FINE_TUNE_PATH, DISEASE_INFO_PATH, INTENTS_PATH) if os.path.exists(p)
        )
        return source_mtime > index_mtime
    except OSError:
        return True


def build_index(force: bool = False) -> None:
    os.makedirs(INDEX_DIR, exist_ok=True)
    if not force and not _index_is_stale():
        return

    documents = build_corpus()
    questions = [d["question"] for d in documents]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=60000,
        min_df=1,
    )
    matrix = vectorizer.fit_transform(questions)

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(matrix, MATRIX_PATH)
    joblib.dump(documents, DOCS_PATH)


class _IndexCache:
    vectorizer = None
    matrix = None
    documents = None


def _ensure_loaded():
    if _IndexCache.vectorizer is not None:
        return
    build_index()
    if not os.path.exists(VECTORIZER_PATH):
        # No data at all — build empty structures so the app doesn't crash.
        _IndexCache.vectorizer = TfidfVectorizer()
        _IndexCache.vectorizer.fit([""])
        _IndexCache.matrix = _IndexCache.vectorizer.transform([""])
        _IndexCache.documents = []
        return
    _IndexCache.vectorizer = joblib.load(VECTORIZER_PATH)
    _IndexCache.matrix = joblib.load(MATRIX_PATH)
    _IndexCache.documents = joblib.load(DOCS_PATH)


def retrieve(query: str, top_k: int = TOP_K_DEFAULT) -> List[RetrievedDoc]:
    """Return the top_k most relevant (question, answer) pairs for the query."""
    _ensure_loaded()
    if not _IndexCache.documents:
        return []

    query_vec = _IndexCache.vectorizer.transform([query])
    sims = cosine_similarity(query_vec, _IndexCache.matrix).flatten()
    top_idx = np.argsort(sims)[::-1][:top_k]

    results = []
    for idx in top_idx:
        score = float(sims[idx])
        if score <= 0.0:
            continue
        doc = _IndexCache.documents[idx]
        results.append(
            RetrievedDoc(question=doc["question"], answer=doc["answer"], source=doc["source"], score=score)
        )
    return results


# ─────────────────────────────────────────────────────────────────────────────
#  3. Symptom extraction + disease prediction (reuses the trained RF model)
# ─────────────────────────────────────────────────────────────────────────────
class _DiseaseModelCache:
    model = None
    label_encoder = None
    symptoms: List[str] = []
    disease_info: Dict = {}
    loaded = False


def _load_disease_model():
    if _DiseaseModelCache.loaded:
        return
    _DiseaseModelCache.loaded = True
    try:
        if os.path.exists(RF_MODEL_PATH):
            _DiseaseModelCache.model = joblib.load(RF_MODEL_PATH)
        if os.path.exists(LABEL_ENCODER_PATH):
            _DiseaseModelCache.label_encoder = joblib.load(LABEL_ENCODER_PATH)
        if os.path.exists(MODEL_METADATA_PATH):
            with open(MODEL_METADATA_PATH, "r") as f:
                meta = json.load(f)
                _DiseaseModelCache.symptoms = meta.get("symptoms", [])
        if os.path.exists(DISEASE_INFO_PATH):
            with open(DISEASE_INFO_PATH, "r") as f:
                _DiseaseModelCache.disease_info = json.load(f)
    except Exception:
        # If anything's missing/corrupt, just disable prediction rather than crash.
        _DiseaseModelCache.model = None


def extract_symptoms(text: str) -> List[str]:
    """Find which of the model's known symptom phrases appear in the user's text."""
    _load_disease_model()
    if not _DiseaseModelCache.symptoms:
        return []
    text_lower = " " + re.sub(r"[^a-z0-9\s]", " ", text.lower()) + " "
    matched = []
    for symptom in _DiseaseModelCache.symptoms:
        phrase = symptom.replace("_", " ")
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(symptom)
    return matched


def predict_disease(matched_symptoms: List[str]) -> Optional[DiseasePrediction]:
    _load_disease_model()
    if not matched_symptoms or _DiseaseModelCache.model is None or _DiseaseModelCache.label_encoder is None:
        return None

    input_vector = [1 if s in matched_symptoms else 0 for s in _DiseaseModelCache.symptoms]
    try:
        proba = _DiseaseModelCache.model.predict_proba([input_vector])[0]
    except Exception:
        return None

    order = np.argsort(proba)[::-1]
    classes = _DiseaseModelCache.label_encoder.classes_

    top_idx = order[0]
    top_disease = classes[top_idx]
    top_conf = float(proba[top_idx]) * 100

    alternatives = [
        {"disease": classes[i], "confidence": round(float(proba[i]) * 100, 1)}
        for i in order[1:4]
        if proba[i] > 0.01
    ]

    info = _DiseaseModelCache.disease_info.get(top_disease)

    return DiseasePrediction(
        disease=top_disease,
        confidence=round(top_conf, 1),
        matched_symptoms=matched_symptoms,
        alternatives=alternatives,
        info=info,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  4. Ollama generation
# ─────────────────────────────────────────────────────────────────────────────
def ollama_is_available(host: str = OLLAMA_HOST) -> bool:
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def list_ollama_models(host: str = OLLAMA_HOST) -> List[str]:
    try:
        r = requests.get(f"{host}/api/tags", timeout=3)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]
    except requests.exceptions.RequestException:
        return []


def _build_prompt(
    user_query: str,
    retrieved: List[RetrievedDoc],
    disease_pred: Optional[DiseasePrediction],
    chat_history: Optional[List[Dict]] = None,
) -> str:
    context_blocks = []
    for i, doc in enumerate(retrieved, start=1):
        snippet = doc.answer[:MAX_CONTEXT_CHARS_PER_DOC]
        context_blocks.append(f"[{i}] Q: {doc.question}\n    A: {snippet}")
    context_text = "\n\n".join(context_blocks) if context_blocks else "No directly relevant reference found."

    prediction_text = ""
    if disease_pred:
        prediction_text = (
            f"\nA symptom-matching model detected these symptoms in the user's message: "
            f"{', '.join(s.replace('_', ' ') for s in disease_pred.matched_symptoms)}.\n"
            f"Its top predicted condition is '{disease_pred.disease}' "
            f"(confidence {disease_pred.confidence}%). "
            f"Treat this as a possibility to mention, NOT a confirmed diagnosis."
        )

    history_text = ""
    if chat_history:
        recent = chat_history[-6:]
        history_text = "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in recent)

    prompt = f"""You are Medora, a careful and empathetic AI health information assistant.
Answer the user's question using the REFERENCE CONTEXT below whenever it's relevant.
If the context doesn't cover the question, answer from general medical knowledge but say so.
Never present yourself as a doctor, never give a definitive diagnosis, and always recommend
professional medical care for anything serious or urgent.
Keep answers concise (roughly 3-6 sentences) and use plain, reassuring language.

REFERENCE CONTEXT:
{context_text}
{prediction_text}

{("CONVERSATION SO FAR:\n" + history_text) if history_text else ""}

USER QUESTION: {user_query}

Answer:"""
    return prompt


def _fallback_answer(retrieved: List[RetrievedDoc], disease_pred: Optional[DiseasePrediction]) -> str:
    """Used when Ollama isn't reachable — build a direct answer from retrieved text only."""
    parts = []
    if disease_pred:
        parts.append(
            f"Based on the symptoms you mentioned ({', '.join(s.replace('_', ' ') for s in disease_pred.matched_symptoms)}), "
            f"the closest match in our data is **{disease_pred.disease}** ({disease_pred.confidence}% confidence). "
            f"This is not a diagnosis — please confirm with a doctor."
        )
        if disease_pred.info:
            parts.append(f"General guidance: {disease_pred.info.get('advice', '')}")

    if retrieved:
        best = retrieved[0]
        snippet = best.answer[:600].rstrip()
        if len(best.answer) > 600:
            snippet += "…"
        parts.append(snippet)
    elif not disease_pred:
        parts.append(
            "I couldn't find a close match for that in our knowledge base. "
            "Please consult a qualified healthcare professional for advice specific to you."
        )

    return "\n\n".join(parts)


def call_ollama(prompt: str, model: str = DEFAULT_OLLAMA_MODEL, host: str = OLLAMA_HOST) -> str:
    response = requests.post(
        f"{host}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


# ─────────────────────────────────────────────────────────────────────────────
#  5. Public entry point used by modules/chatbot.py
# ─────────────────────────────────────────────────────────────────────────────
def answer(
    user_query: str,
    chat_history: Optional[List[Dict]] = None,
    top_k: int = TOP_K_DEFAULT,
    ollama_model: str = DEFAULT_OLLAMA_MODEL,
    ollama_host: str = OLLAMA_HOST,
    use_llm: bool = True,
) -> RagResult:
    retrieved = retrieve(user_query, top_k=top_k)

    matched_symptoms = extract_symptoms(user_query)
    disease_pred = predict_disease(matched_symptoms) if matched_symptoms else None

    if use_llm:
        try:
            prompt = _build_prompt(user_query, retrieved, disease_pred, chat_history)
            llm_text = call_ollama(prompt, model=ollama_model, host=ollama_host)
            if llm_text:
                return RagResult(
                    answer=llm_text,
                    sources=retrieved,
                    disease_prediction=disease_pred,
                    used_llm=True,
                )
        except requests.exceptions.RequestException as e:
            fallback = _fallback_answer(retrieved, disease_pred)
            return RagResult(
                answer=fallback,
                sources=retrieved,
                disease_prediction=disease_pred,
                used_llm=False,
                llm_error=str(e),
            )

    fallback = _fallback_answer(retrieved, disease_pred)
    return RagResult(
        answer=fallback,
        sources=retrieved,
        disease_prediction=disease_pred,
        used_llm=False,
    )
