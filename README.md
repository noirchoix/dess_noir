# DESS Bridge Physics Lab

Portfolio App 2 in the chemistry deployment series.

This is a **FastAPI + SvelteKit** lab-console application for exploring DESS bridge physics artifacts. It exposes stored DESS66x8 outputs, QC status, metric summaries, SAPT/CCSD(T)-style prediction rows, reactant/product physics scores, candidate rank scores, and an explanation layer for interpreting a scoring run.

The app is designed for clean portfolio deployment: GitHub stores source code only, while the DESS artifact bundle is hosted on Hugging Face and downloaded into a local runtime cache.

## Portfolio positioning

This app demonstrates artifact-backed scientific ML deployment. It is not presented as a live DESS graph-neural-network inference engine. Exact artifact matches use stored DESS bridge scores; new SMILES use a deterministic artifact-calibrated prior unless a future live inference adapter is added.

Scientific disclaimer: this app is a portfolio/demo tool for physics-informed chemistry exploration. It is not laboratory validation, regulatory validation, or production formulation approval software. Scores should be treated as screening and prioritization signals.

## Stack

- Backend: FastAPI
- Frontend: SvelteKit
- Data runtime: DuckDB, Parquet, JSON
- Optional explanation layer: offline by default, DeepSeek or Gemini if configured
- Artifact hosting: Hugging Face dataset repo

## Runtime endpoints

```text
GET  /
GET  /api/v1/dess/health
GET  /api/v1/dess/summary
GET  /api/v1/dess/metrics
GET  /api/v1/dess/predictions?limit=40
GET  /api/v1/dess/reactants
GET  /api/v1/dess/products
GET  /api/v1/dess/ranks
POST /api/v1/dess/score
POST /api/v1/dess/explain
```

## Hugging Face assets

Dataset repo:

```text
noirchoix/dess-bridge-physics-lab
```

Upload the full logical contents of `apps/api/data/dess_physics/` to that Hugging Face dataset repo, preserving paths exactly:

```text
dess_physics/curated/v1/candidate_rank_scores.parquet
dess_physics/curated/v1/dess_target_predictions.parquet
dess_physics/curated/v1/inputs/candidate_inputs.parquet
dess_physics/curated/v1/inputs/inputs_manifest.json
dess_physics/curated/v1/inputs/reactant_inputs.parquet
dess_physics/curated/v1/model/artifact_manifest.json
dess_physics/curated/v1/model/audit.json
dess_physics/curated/v1/model/config.normalized.json
dess_physics/curated/v1/model/dess66x8_v2.pt
dess_physics/curated/v1/model/dess66x8_v2_best.pt
dess_physics/curated/v1/model/dess66x8_v2_metrics.json
dess_physics/curated/v1/model/dess66x8_v2_test_preds.csv
dess_physics/curated/v1/model/dess66x8_v2_trial001_audit.json
dess_physics/curated/v1/model/metrics.json
dess_physics/curated/v1/physics_stats.json
dess_physics/curated/v1/product_physics_scores.parquet
dess_physics/curated/v1/qc_report.json
dess_physics/curated/v1/raw_dess_predictions.parquet
dess_physics/curated/v1/reactant_physics_scores.parquet
dess_physics/staging/dess_physics.duckdb
```

Suggested upload command from `apps/api/data` in the original artifact-bearing copy:

```bash
huggingface-cli upload noirchoix/dess-bridge-physics-lab dess_physics dess_physics --repo-type dataset
```

## Backend setup

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On first startup, the backend checks `DESS_ASSET_CACHE_DIR`. If any required artifact is missing, it downloads the missing files from Hugging Face. The default cache path is `apps/api/data`, which is intentionally ignored by Git.

## Frontend setup

```bash
cd apps/web
npm install
npm run dev -- --host 0.0.0.0
```

Open:

```text
http://localhost:5173
```

## Environment variables

Backend:

```env
DESS_ASSET_REPO_ID=noirchoix/dess-bridge-physics-lab
DESS_ASSET_REPO_TYPE=dataset
DESS_ASSET_CACHE_DIR=./data
HF_DOWNLOAD_ENABLED=true
DESS_DUCKDB_PATH=./data/dess_physics/staging/dess_physics.duckdb
DESS_CURATED_DIR=./data/dess_physics/curated/v1
FRONTEND_ORIGIN=http://localhost:5173
DESS_MAX_LIMIT=500
LLM_PROVIDER=offline
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-chat
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

Frontend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Validation

Backend syntax check:

```bash
cd apps/api
python -m compileall .
```

Backend smoke test, after model/data artifacts are local or downloadable from Hugging Face:

```bash
cd apps/api
uvicorn main:app --host 0.0.0.0 --port 8000
python tests/smoke_test.py
```

Frontend:

```bash
cd apps/web
npm install
npm run build
```

## Deployment recommendation

Recommended portfolio setup:

- Backend: Render, Railway, or Fly.io
- Frontend: Vercel or Netlify
- Artifacts: Hugging Face dataset repo

Set the backend deployment environment:

```env
DESS_ASSET_REPO_ID=noirchoix/dess-bridge-physics-lab
DESS_ASSET_REPO_TYPE=dataset
DESS_ASSET_CACHE_DIR=./data
HF_DOWNLOAD_ENABLED=true
DESS_DUCKDB_PATH=./data/dess_physics/staging/dess_physics.duckdb
DESS_CURATED_DIR=./data/dess_physics/curated/v1
FRONTEND_ORIGIN=https://your-frontend-url.netlify.app
LLM_PROVIDER=offline
```

Set the frontend deployment environment:

```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

If you enable the optional explanation layer, use deployment secrets for `DEEPSEEK_API_KEY` or `GEMINI_API_KEY`. Do not commit real keys.
