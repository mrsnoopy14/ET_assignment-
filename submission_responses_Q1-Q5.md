# Expert Thermal – Assessment Responses

Shashi Shekhar  
shekharshashi127@gmail.com | +91 9199612567  
Date: 2026-01-29

This submission includes (1) a validated thermal model + Flask API, and (2) written responses for the remaining questions.

## 1) Python Model + Flask

### What I built
- A Python implementation of the step-by-step resistance-network method in `Thermal_Reference.pdf`.
- A validation script that compares Python outputs to the provided Excel reference workbook (`3. Heat_Sink_Design_Ref.xlsx`).
- A small Flask API so the model can be called programmatically.

Code artifacts in this folder:
- Model: `src/thermal_model.py`
- API: `src/app.py`
- Excel validation: `validate_against_excel.py`
- Output snapshot: `out/show_results.json`

### Model summary
The model follows the same resistance-network structure as the reference:

- \(R_{total} = R_{jc} + R_{TIM} + R_{hs}\)
- \(R_{hs} = R_{cond} + R_{conv}\)
- \(T_j = T_{amb} + Q\,R_{total}\)

With:
- \(R_{TIM} = t_{TIM} / (k_{TIM} A_{die})\)
- \(R_{cond} = t_b / (k_{Al} A_{die})\)
- \(R_{conv} = 1 / (h A_{total})\)

For forced convection, the model follows the reference’s correlation choice based on Reynolds number:
- Fin spacing \(S_f = (W - N\,t_f)/(N-1)\)
- Reynolds \(Re = V S_f / \nu\)
- If \(Re < 2300\): \(Nu = 1.86 (Re\,Pr\,(2S_f/L))^{1/3}\)
- Else: \(Nu = 0.023 Re^{0.8} Pr^{0.3}\)
- \(h = Nu\,k_{air}/(2S_f)\)

### Validation against Excel
- The validator reads the reference outputs from `Sheet1` and compares them to the Python model.
- Cells used:
  - `I37`: total resistance (R_total)
  - `I38`: junction temperature (T_junction)
  - Intermediate checks: `I30` (R_conv), `I29` (R_cond), `I26` (R_TIM)

The latest run output (Python + Excel side-by-side) is saved in `out/show_results.json`.

### How to run
Validate vs Excel:
- `python validate_against_excel.py --tol-r 0.001 --tol-t 0.01`

Start the Flask API:
- `python src/app.py`

Endpoints:
- `GET /thermal` – returns results for default inputs.
- `POST /thermal` – override any input fields via JSON.

Example POST payload (override air velocity):
```json
{ "air_velocity_m_s": 2.0 }
```

---

## 2) PINN Understanding + Application

### High-level formulation (for this thermal problem)
A Physics-Informed Neural Network (PINN) would approximate the temperature field \(T(x,y,z)\) (or a reduced model like \(T(x,y)\) or 1D \(T(z)\)) and be trained so its predictions satisfy the physics:
- Governing PDE (steady conduction): \(\nabla \cdot (k \nabla T) + q''' = 0\) in solids (die/TIM/base/fins)
- Boundary conditions:
  - Prescribed heat flux on die contact region (or volumetric generation in die)
  - Convection boundary on exposed heat sink surfaces: \(-k\,\partial T/\partial n = h\,(T - T_{amb})\)
  - Interface continuity between layers: continuity of temperature and heat flux

#### Inputs / outputs
- Inputs: spatial coordinates (and optionally parameters) e.g. \((x,y,z)\) and parameters \(\theta\) such as \(V\), fin geometry, \(k\) values.
- Outputs: temperature \(T\). Optionally also predict auxiliary fields (e.g., heat flux) if helpful.

#### Loss terms
- PDE residual loss in each domain
- Boundary loss terms for flux and convection conditions
- Interface loss terms enforcing continuity
- Optional supervised loss using sparse points from the existing lumped model (or CFD/FEM) to stabilize training

#### Training data
- Collocation points sampled in each solid region + on each boundary surface.
- No labeled temperature required for a pure PINN, but adding a small supervised set (hybrid PINN) can improve convergence.

### My background and ramp-up plan (new to PINNs)
I’m new to PINNs. My plan is to get to a working prototype quickly while keeping validation tight:
- **Time budget:** ~6–10 hours to get working intuition + 1–2 days to prototype/iterate.
- **Read/watch:** introductory PINN material (what the residual losses mean, how boundary conditions are enforced), plus a couple of reference implementations.
- **Libraries:** start with PyTorch (or JAX) directly for transparency; optionally use DeepXDE to accelerate experimentation once the baseline works.
- **Validation mindset:** use the existing validated resistance-network model as a baseline and sanity check at each step.

### Practical plan to apply a PINN here
Because the provided reference model is a lumped resistance network (i.e., it produces reliable scalar outputs like \(T_j\) and effective resistances), a sensible progression is:
1) Start with a reduced-order PDE (e.g., 1D through-thickness stack: die → TIM → base) with a convection boundary at the top.
2) Validate PINN outputs against:
   - The analytic / resistance-network temperature drops (what we implemented)
   - The Excel reference outputs (junction temperature / resistances)
3) Expand complexity only if needed:
   - 2D/3D base spreading + convection
   - Include fin geometry explicitly (or use an effective h/A approach)

### Concrete PINN prototype outline (first shot)
To keep scope realistic and aligned with the provided reference, I would start with a **1D steady conduction** stack (die → TIM → base) and a convection boundary at the exposed surface:
- **Network:** MLP that maps depth coordinate \(z\) to temperature \(T(z)\).
- **Physics loss:** enforce \(d/dz (k\, dT/dz) = 0\) in each layer (piecewise constant \(k\)).
- **Interface loss:** continuity of temperature and heat flux at layer boundaries.
- **Boundary loss:** imposed heat flux at the die side and convection \(-k\,dT/dz = h\,(T - T_{amb})\) at the exposed surface.
- **Validation:** compare predicted \(T\) drops and \(T_j\) vs the existing Python resistance model and the Excel reference outputs.

Once the 1D version is stable and validated, I’d only expand to 2D/3D if the product needs spatial temperature maps (hotspots/spreading) rather than a single junction temperature and effective resistances.

---

## 3) Vertex AI Exposure / Understanding

I don’t have direct hands-on experience with Google Vertex AI, but I understand the role it plays in deploying and operating ML/GenAI systems.

Vertex AI is Google Cloud’s managed ML/GenAI platform used to:
- Train and deploy ML models (custom training, model registry, endpoints)
- Use and operationalize foundation models (Gemini, embeddings) for GenAI apps
- Build RAG pipelines (vector search via Vertex AI Search / embeddings + retrieval + prompting)
- Orchestrate MLOps (pipelines, monitoring, evaluation)

In an engineering/product-focused GenAI context, Vertex AI can support:
- Chat/assistants over engineering docs (RAG)
- Automated report generation and summarization of simulation/design results
- Model evaluation, safety filters, and deployment pipelines

---

## 4) Motivation & Passion

I’m excited about Expert Thermal because it combines rigorous engineering with real product impact—turning thermal models into tools that are reliable, testable, and easy to integrate. I like owning work end-to-end (model → validation → API) and I’m comfortable shipping production-grade systems (APIs, Docker, CI/CD). I’m especially motivated to grow into physics-aware ML (starting with PINNs) and build platform features that accelerate engineering workflows in a fast-moving team.

---

## 5) Web Development Ownership (Node.js / React.js)

I have hands-on experience with both backend and frontend development, and I’m comfortable taking ownership of full-stack features.

- **Backend (Node.js/Express):** Built and optimized REST APIs with JWT authentication, improved latency, containerized services with Docker, and set up CI/CD (e.g., Jenkins) during a startup internship.
- **Frontend (React/Next.js):** Built reusable UI components and integrated REST APIs; also worked on performance improvements (e.g., page load reductions) during my IBM internship.
- **Project ownership:** I’ve built full-stack applications end-to-end (Node/Express + React/Next.js + SQL/NoSQL) including schema design, CRUD workflows, role-based access, and dashboards.

When taking ownership of an existing Node.js/React codebase, my approach is:
- Get a clean local run (env vars, database, seed, build) and reproduce issues quickly.
- Map core flows (auth, critical routes, key UI paths), then add small guardrails (logging, a couple of tests) around the hottest paths.
- Make targeted, incremental changes with clear verification steps and keep deployment safe with Docker + CI/CD.

I’m confident I can debug and ship fixes quickly in a fast-moving environment.

---
