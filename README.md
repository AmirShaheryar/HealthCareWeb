# NLP-Medora — AI Health Management Dashboard
### NUCES FAST | CS Project | Shaheryar Amir 23L-0828 & Muhammad Saad 22L-6852

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App
```bash
streamlit run app.py
```

The app will open at: `http://localhost:8501`

---

## 🔐 Demo Credentials

| Role    | Email                | Password    |
|---------|----------------------|-------------|
| Patient | patient@demo.com     | patient123  |
| Doctor  | doctor@demo.com      | doctor123   |
| Admin   | admin@demo.com       | admin123    |

---

## 📋 Features Implemented (All 15 Requirements)

| # | Feature | Status |
|---|---------|--------|
| 1 | Multi-Role Authentication | ✅ |
| 2 | Role-Based Profile Management | ✅ |
| 3 | Admin Control Panel | ✅ |
| 4 | Basic Health Dashboard | ✅ |
| 5 | Symptom Information Display | ✅ |
| 6 | Chatbot Health Assistant | ✅ |
| 7 | Voice-to-Text + SOAP Notes | ✅ |
| 8 | Clinical Prediction Review (Doctor) | ✅ |
| 9 | Medical Report Simplification | ✅ |
| 10 | Symptom-to-Disease Mapping | ✅ |
| 11 | Sentiment & Emotion Detection | ✅ |
| 12 | Price-Aware Nutrition Suggestions | ✅ |
| 13 | Health vs. Wealth Visualization | ✅ |
| 14 | RAG Q&A (TF-IDF retrieval + local LLM via Ollama) | ✅ |
| 15 | Genetic & AQI Environmental Analysis | ✅ |

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **Streamlit** — UI framework
- **Plotly** — Interactive charts
- **Pandas / NumPy** — Data processing
- **NLP** — Custom rule-based extraction (spaCy-ready)

---

## 🤖 RAG Chatbot — How it works & how to run it

`modules/chatbot.py` is now a full Retrieval-Augmented Generation pipeline (`services/rag_engine.py`),
not a keyword-matching bot:

1. **Knowledge base**: `data/fine_tune_data.jsonl` (~28.5k medical Q&A pairs), `model/disease_info.json`,
   and `data/intents.json` are combined into one corpus.
2. **Retrieval**: a TF-IDF index (scikit-learn) over the corpus is built on first run and cached to
   `model/rag_index/` (rebuilds automatically if the source data files change, or manually via the
   "🔄 Rebuild knowledge index" button in the chatbot sidebar). No extra downloads required.
3. **Symptom → disease check**: if the user's message mentions known symptom phrases, they're run through
   the existing trained model (`model/disease_rf_model.pkl`) to surface a probable condition alongside
   the answer (clearly labeled as a model match, not a diagnosis).
4. **Generation**: the retrieved context + symptom check + recent chat history are assembled into a
   prompt and sent to a **locally running Ollama model** for the final natural-language answer. If
   Ollama isn't reachable, the chatbot automatically falls back to showing the best-matching retrieved
   text directly, so it still works with zero setup.

### Running with Ollama (recommended, for LLM-generated answers)
```bash
# 1. Install Ollama: https://ollama.com/download
# 2. Pull a model (any chat model works; llama3.2 is the default the app looks for)
ollama pull llama3.2
# 3. Make sure the Ollama server is running (it usually starts automatically)
ollama serve
# 4. Run the app as usual
streamlit run app.py
```
In the chatbot's sidebar you can change the Ollama host/model, adjust how many chunks are retrieved,
or turn LLM generation off entirely (pure retrieval mode).

You can also configure defaults via environment variables instead of the sidebar:
```bash
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="llama3.2"
```
