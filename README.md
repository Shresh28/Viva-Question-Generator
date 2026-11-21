# VivaPrep AI

**Prepare smarter. Defend your project confidently.** VivaPrep AI reads a project report PDF and prepares a report-grounded practice set: exactly 15 viva questions with short answers, split into 5 Easy, 5 Medium, and 5 Hard questions.

## Problem statement

Students often have difficulty anticipating the questions an examiner may ask about their project. VivaPrep AI uses the report itself as evidence to prepare questions about the project's purpose, design, implementation, and technical trade-offs. It asks the model to acknowledge missing details instead of making them up, and validates the returned structure before showing it.

## Features

- PDF filename, page count, readable-text status, extraction cleanup, and scanned-PDF/OCR guidance.
- Local model question generation grounded in the uploaded report.
- Exactly 5 questions at each of three difficulty levels; duplicates and malformed responses are rejected.
- Short or Detailed answer style, result persistence during the browser session, and regeneration.
- Expandable answer cards, extracted-text transparency, TXT downloads, and PDF downloads.
- Local generation through Ollama, which keeps report text on this computer.
- Friendly handling for local model/service errors, malformed PDFs, and file-size limits.
- Modular services and a mocked pytest suite.

## Technology stack

Python 3.10+, Streamlit, PyPDF2, Ollama's local HTTP API, python-dotenv, requests, ReportLab, and pytest. The app uses the `llama3.2:latest` model downloaded through Ollama by default; configure `OLLAMA_MODEL` in `.env` to use another installed model.

## Architecture and workflow

1. Streamlit accepts a PDF and enforces the configured upload limit.
2. `src/pdf_processor.py` extracts and cleans text with PyPDF2. PDFs with no selectable text get an OCR recommendation.
3. `src/prompt_builder.py` assembles a separate system prompt and report prompt.
4. `src/ai_generator.py` calls Ollama on the local computer and maps service/model failures to safe user-facing errors.
5. `src/output_parser.py` validates project metadata, required fields, exactly 15 questions, 5 per difficulty, and duplicates.
6. Streamlit displays the validated set; `src/exporters.py` produces TXT and PDF downloads.

Report text is sent to the Ollama service on your computer and is not sent to a cloud provider by this app.

## Project structure

```text
VivaPrepAI/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── ai_generator.py
│   ├── exporters.py
│   ├── output_parser.py
│   ├── pdf_processor.py
│   └── prompt_builder.py
├── tests/
│   ├── manual_checklist.md
│   ├── test_ai_generator.py
│   ├── test_exporters.py
│   ├── test_output_parser.py
│   ├── test_pdf_processor.py
│   └── test_prompt_builder.py
└── screenshots/
```

## Installation on Windows

Open PowerShell in the project folder. Install Python 3.10 or newer first, then run:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks environment activation, use this for the current terminal only, then activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Ollama setup

Ollama runs supported models on your computer with no cloud API key or per-request charge. Generation speed and answer quality depend on your computer and the model size. Install Ollama for Windows from [ollama.com/download](https://ollama.com/download), then open PowerShell and download a model:

```powershell
ollama pull llama3.2:latest
```

Ollama normally runs as a local service after installation. This project uses `llama3.2:latest` by default. If needed, set `OLLAMA_BASE_URL=http://localhost:11434` and `OLLAMA_MODEL=llama3.2:latest` in `.env`. See the [Ollama model library](https://ollama.com/library) for other models. Model downloads need internet once; subsequent inference runs locally.

## Run the application

With Ollama running, the model downloaded, and the virtual environment active:

```powershell
streamlit run app.py
```

Streamlit prints a local address, usually `http://localhost:8501`, and opens the app in your browser.

## How to use

1. Upload a searchable project report PDF (maximum 25 MB by default).
2. Check its filename, page count, and text extraction. If it is scanned, OCR it first and upload a searchable PDF.
3. Choose Short or Detailed answers and click **Generate Viva Questions**.
4. Review the project snapshot and Easy, Medium, and Hard tabs. Expand a card to see its suggested answer.
5. Download the set as TXT or PDF. Click **Regenerate Questions** to request another set for the same report.

The extracted text can be inspected in the **Show extracted report text** section. Very long reports are shortened to the beginning and ending sections before sending to the model.

## Testing

```powershell
python -m pytest -q
python -m compileall -q app.py src tests
```

Automated generation tests use a fake Ollama response and require no model download or network call. They validate application behavior, not live model response quality. Complete [tests/manual_checklist.md](tests/manual_checklist.md) with real reports from five project domains before claiming the manual checks passed.

## Known limitations

- PyPDF2 extracts selectable text; scanned/image-only PDFs require OCR in another tool first.
- Very long reports are truncated to their opening and closing sections to keep requests manageable, so relevant details in the middle may be missed.
- Local model output is generated content and should be checked against the original report before a viva.
- PDF export uses a built-in Latin font; glyphs outside Latin-1 may appear as replacement characters. The TXT export preserves Unicode.
- Automated tests do not prove factual quality for your report or model/API availability.



## Future scope

- Optional OCR integration for scanned reports.
- Citation hints that link each generated question to report sections or pages.
- Optional support for additional local model providers.
- Export customization and user-selected question counts while preserving balanced difficulty.

## GitHub readiness

The project is published in the GitHub repository. For future updates, review `git status` before committing. `.env`, PDF files, virtual environments, Python caches, and generated text files are ignored.

SHRESH BURHANPURKAR 

