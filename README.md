# ⚖️ LegalLens: Citation-Grounded Legal Document Auditing Pipeline

**LegalLens** is a 100% Python-based, citation-grounded legal document auditing pipeline and interactive web application. It ingests contracts (digital PDFs, scanned documents, and handwritten agreements), extracts and chunks legal text, grounds clauses against a local vector database of high-risk benchmarks, and performs rigid schema-enforced risk audits powered by the Google Gemini API.

---

## 🚀 Key Features

- **Document & Handwriting OCR (PaddleOCR)**: Seamlessly processes digital PDFs as well as scanned contracts, stamped agreements, and handwritten annotations.
- **Context-Aware Legal Chunking (LangChain)**: Splits contracts by legal boundaries (Articles, Sections, numbered clauses) using `RecursiveCharacterTextSplitter`.
- **Local Benchmark Grounding (ChromaDB + Sentence-Transformers)**: Embedded local vector database (`./chroma_legal_db`) seeded with predatory benchmarks and standard boilerplate from `data/risk_playbook.json` using `all-MiniLM-L6-v2`.
- **Rigid Schema Enforcement (Google Gemini + Pydantic)**: Enforces strict structured JSON schema with Pydantic validation for every audited clause:
  - **Risk Tiers**: 🚨 `High Risk`, ⚠️ `Moderate Risk`, and ✅ `Safe`
  - **Risk Scores**: 1 (benign) to 10 (severely predatory)
  - **Plain-English Explanations**: Business-oriented translation of real-world exposure
  - **Citations & Benchmarks**: Grounded against specific legal doctrines (UCC, Restatement, FTC) and Playbook IDs (e.g., `PB-001`)
  - **Actionable Redlines**: Ready-to-use counter-proposals and balanced revisions
- **Executive Streamlit Dashboard**:
  - Overall Contract Risk Index (1–100)
  - Interactive risk-tier filter pills and search bar
  - Instant pre-loaded predatory contract benchmarks for quick testing
  - One-click export to structured JSON or Markdown reports

---

## 🏗️ Architecture & Project Structure

```
LEGALLENS/
├── data/
│   ├── risk_playbook.json       # 10 Benchmark clauses (High Risk, Moderate, Safe)
│   └── sample_contracts.py      # Preloaded sample predatory & balanced agreements
├── modules/
│   ├── __init__.py
│   ├── ocr_parser.py            # PDF/Image ingestion, PaddleOCR & LangChain chunker
│   ├── vector_store.py          # ChromaDB persistent store & MiniLM embeddings
│   └── auditor.py               # Gemini LLM runner & Pydantic schema validation
├── chroma_legal_db/             # Local ChromaDB persistent vector storage (auto-created)
├── app.py                       # Main Streamlit dashboard
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment configuration template
└── README.md                    # Project documentation
```

---

## 🛠️ Quickstart Installation

### 1. Clone or Open Project
```bash
cd LEGALLENS
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note for PaddlePaddle on Windows:**
> If you have a dedicated NVIDIA GPU, you can optionally install `paddlepaddle-gpu`. For standard CPU execution, `paddlepaddle` from `requirements.txt` runs out-of-the-box.

### 4. Configure Google Gemini API Key
Create a `.env` file from the template:
```bash
copy .env.example .env
```
Add your Gemini API key:
```env
GEMINI_API_KEY=AIzaSy...
```
*(You can also enter your key directly inside the LegalLens web interface sidebar).*

---

## 🖥️ Running LegalLens

Start the Streamlit application:
```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Testing with Sample Contracts

No PDF at hand? Click either of the built-in sample loader buttons in the dashboard:
1. **🚨 Load Predatory SaaS Contract**: Tests unilateral uncapped indemnity, offshore 100% cost-shifting arbitration, evergreen auto-renewal traps, and a 7-year worldwide non-compete.
2. **🛡️ Load Balanced Mutual NDA**: Tests standard mutual confidentiality, customary carve-outs, and reasonable liability limits.
