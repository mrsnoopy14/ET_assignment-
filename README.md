# Expert Thermal – Assessment Submission

This repo contains:
- A Python thermal resistance-network model derived from the provided reference.
- Validation against the provided Excel reference workbook.
- A Flask API wrapper for programmatic use.
- Written responses in `submission_responses_Q1-Q5.md`.

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

## Local Node.js service (calls Python solver API)

The challenge add-on is implemented in `node-service/`. It runs locally and forwards JSON requests to the Flask solver.

### 1) Start the Python solver

In one terminal:

```bash
python src/app.py
```

### 2) Start the Node service

In a second terminal:

```bash
cd node-service
npm install
npm start
```

By default it calls `http://127.0.0.1:5000/thermal`.

### 3) Test (for screenshots)

Default solver call:

```bash
curl http://127.0.0.1:3000/solve/default
```

Note (Windows PowerShell): `curl` may be an alias for `Invoke-WebRequest`. If you hit issues, use either:

```powershell
Invoke-RestMethod http://127.0.0.1:3000/solve/default
```

POST JSON to solver:

```bash
curl -X POST http://127.0.0.1:3000/solve -H "Content-Type: application/json" -d @node-service/sample_request.json
```

PowerShell equivalent:

```powershell
$body = Get-Content node-service/sample_request.json -Raw
Invoke-RestMethod http://127.0.0.1:3000/solve -Method Post -ContentType 'application/json' -Body $body
```

Optional: override the solver URL if you change the Flask port:

```bash
set SOLVER_URL=http://127.0.0.1:5000/thermal
npm start
```

## Project layout

- `src/thermal_model.py` – core thermal model
- `src/app.py` – Flask API
- `validate_against_excel.py` – Excel validation script
- `show_results.py` – writes a Python-vs-Excel snapshot to `out/show_results.json`
- `submission_responses_Q1-Q5.md` – written answers

## Note on provided files
The PDFs/XLSX references are treated as local inputs and are ignored by `.gitignore` by default to avoid accidentally publishing proprietary content.
If you are submitting as a private repo and want to include them, remove the relevant patterns from `.gitignore`.
