# Expert Thermal – Assessment Submission

This repo contains:
- A Python thermal resistance-network model derived from the provided reference.
- Validation against the provided Excel reference workbook.
- A Flask API wrapper for programmatic use.
- Written responses in `submission_responses.md`.

## Quick start

### 1) Create/activate venv
If you already have `.venv` in this folder, you can reuse it.

### 2) Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Validate vs Excel

```bash
python validate_against_excel.py --tol-r 0.001 --tol-t 0.01
```

This compares the Python model against cached numeric outputs in the provided workbook `3. Heat_Sink_Design_Ref.xlsx` (Sheet1 reference cells).

## Run the Flask API

```bash
python src/app.py
```

Endpoints:
- `GET /thermal` returns results for default inputs.
- `POST /thermal` accepts JSON overrides.

Example:

```bash
curl -X POST http://127.0.0.1:5000/thermal -H "Content-Type: application/json" -d "{\"air_velocity_m_s\": 2.0}"
```

## Project layout

- `src/thermal_model.py` – core thermal model
- `src/app.py` – Flask API
- `validate_against_excel.py` – Excel validation script
- `out/show_results.json` – latest run snapshot (local output)
- `submission_responses.md` – written answers

## Note on provided files
The PDFs/XLSX references are treated as local inputs and are ignored by `.gitignore` by default to avoid accidentally publishing proprietary content.
If you are submitting as a private repo and want to include them, remove the relevant patterns from `.gitignore`.
