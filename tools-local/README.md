# Dev Tools

A collection of local developer utilities served as a **FastAPI web app** with a single-page frontend and a **Click CLI** for select tools.

## Tools

| Tool | Description | CLI |
|------|-------------|-----|
| Token Calculator | Estimate token counts and API costs across LLMs | `tokens` |
| JSON Linter | Validate and pretty-print JSON | `json-format` |
| File Renamer | Batch rename files with pattern rules | - |
| Excel Reader | View and convert Excel files to CSV | `excel-to-csv` |
| Image Tools | Resize, convert, and edit images | - |
| Storage Analyzer | Analyze disk usage for a given directory | - |
| Network Scanner | Discover devices on the local network | - |
| ChatGPT Viewer | Browse and search exported ChatGPT conversations | - |
| Gemini Chat | Interact with the Gemini API | - |
| Audio Transcription | Transcribe audio files locally | - |
| Markdown Converter | Convert Markdown to HTML/PDF | - |

## Getting Started

```bash
# Create a virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Web App

```bash
python run.py
# Open http://127.0.0.1:5777
```

### CLI

```bash
python cli.py tokens --text "Hello world"
python cli.py tokens --file document.pdf --model gpt-4
python cli.py json-format data.json
python cli.py excel-to-csv spreadsheet.xlsx --output result.csv
```

## Project Structure

```
app/                   # Backend — one package per tool
  main.py              # FastAPI app factory, registers all routers
  token_calculator/    # Each tool has routes.py + core modules
  json_linter/
  ...
static/                # Frontend — vanilla HTML/CSS/JS SPA
  index.html           # All tool pages in a single file
  js/                  # Shell routing + per-tool scripts
  css/                 # Theme, layout, and shared styles
config/
  models.json          # LLM model definitions for token calculator
cli.py                 # Click CLI entry point
run.py                 # Uvicorn runner
requirements.txt
```

## Architecture

- **Backend**: Each tool lives under `app/<tool>/` with a `routes.py` (FastAPI router) wrapping framework-agnostic core modules. API routes are namespaced (e.g. `/api/token-calculator/`, `/api/json-linter/`).
- **Frontend**: Hash-based SPA routing with no build step. Dark/light theme toggle persisted via `localStorage`.
- **CLI**: Shares core logic with the web app by importing directly from `app/<tool>/` modules.
- **Stateless**: No database. ChatGPT Viewer uses a local JSON file cache in `chatgpt-convo/.cache/`.

## Requirements

- Python 3.11+
- See `requirements.txt` for all dependencies
