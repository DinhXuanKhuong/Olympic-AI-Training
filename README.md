# Exam Practice

A React + FastAPI exam-practice website based on the approved designs in `stitch_exampractice_platform/`. The frontend has flashcards, 60-minute exams, 180-minute exams, and answer review. Questions are edited as JSON and imported into SQLite for the running app.

The easiest setup uses **one address**: FastAPI serves both the built website and `/api`. You can open that address locally or expose it with ngrok.

## Requirements

- Python 3.10 or newer, with `venv` and `pip`
- Node.js 20 or newer and npm
- ngrok agent and an ngrok account **only** for public access

Run the commands below from the repository root unless a command starts with `cd`.

## 1. Run the website locally

### Install and build the frontend

```bash
cd frontend
npm install
VITE_API_BASE_URL= npm run build
cd ..
```

The build creates `frontend/dist/`, which FastAPI serves. You do **not** need `npm run dev` for this one-port setup.

### Install and prepare the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
python scripts/import_questions.py
```

The `test -f` command creates `backend/.env` only when it is missing, preserving an existing ngrok token and other settings.

### Start the website

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open **http://localhost:8000/**. The same server provides:

| Address | Purpose |
| --- | --- |
| `http://localhost:8000/` | Website |
| `http://localhost:8000/api/health` | API health check; returns `{"status":"ok"}` |
| `http://localhost:8000/docs` | Interactive API documentation |

Keep that terminal running while using the site. Stop it with Ctrl+C.

> On Debian or Ubuntu, if creating the virtual environment fails with `ensurepip is not available`, install the system `python3-venv` package, then create `.venv` again.

## 2. Put the website online with ngrok

Complete the local installation above, including `npm install`, the backend dependencies, and the question import. Install the [ngrok agent](https://ngrok.com/download) so the `ngrok` command is available.

Get your authtoken from your [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken). Open **`backend/.env` in an editor** and set:

```dotenv
NGROK_AUTHTOKEN=your_actual_token
```

The token belongs in `backend/.env`, **never** in `frontend/.env` or a `VITE_` variable. `backend/.env` is ignored by Git. You do not need to run `ngrok config add-authtoken`.

Stop any existing server using port 8000. Then, from `backend/`, run:

```bash
./run_backend.sh
```

The script builds the frontend, starts FastAPI, starts ngrok, and prints something like:

```text
PUBLIC WEBSITE URL
https://example.ngrok-free.dev/
API: https://example.ngrok-free.dev/api
Swagger: https://example.ngrok-free.dev/docs
```

**Open the exact `PUBLIC WEBSITE URL` printed by your script.** The address shown above is only an example; your assigned address may differ or change on restart. Keep the script running to keep the site online. Ctrl+C stops both FastAPI and ngrok.

For this public setup, **do not set `VITE_API_BASE_URL` to the ngrok URL**. The production website calls `/api` on its own origin. Changing `VITE_API_BASE_URL` does not publish a website; it only changes where a separately running frontend sends API requests.

## Optional: develop with Vite on a separate port

Use this only when you want Vite's hot reload. Start the backend in one terminal:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, start Vite:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open **http://localhost:5173/**. For this setup, `frontend/.env` should contain:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

If `frontend/.env` already exists, edit its value instead of copying the example over it. Restart Vite after changing the file. `backend/.env` contains `FRONTEND_ORIGINS`; add the exact Vite page origin there if you serve Vite from a different address. The launcher explicitly builds with an empty API base URL. For ordinary production builds, `frontend/.env.production` also sets an empty value so requests use same-origin `/api` even when the development `.env` points elsewhere.

## Question bank

`backend/question_bank/` contains six **illustrative sample files**, totaling 120 questions. They are tagged `sample-bank`; replace them with your own material before serious study. Each `.json` file contains an array of question objects:

```json
[
  {
    "id": "dl_0001",
    "question": "Which activation function outputs zero for negative inputs?",
    "option_a": "Sigmoid",
    "option_b": "ReLU",
    "option_c": "Softmax",
    "option_d": "Linear",
    "correct_answer": "B",
    "category": "Deep Learning",
    "subcategory": "Neural Networks",
    "difficulty": "easy",
    "tags": ["activation-functions", "relu"]
  }
]
```

IDs must be globally unique. `correct_answer` must be `A`, `B`, `C`, or `D`; `difficulty` must be `easy`, `medium`, or `hard`. Tags are arrays of strings. The importer trims and normalizes tags, rejects malformed data, inserts new questions, updates changed ones, and removes database questions deleted from JSON.

After **every** question-bank edit, run:

```bash
cd backend
source .venv/bin/activate
python scripts/import_questions.py
```

New JSON files and categories appear in the website after import; no frontend source change is needed. The importer prints counts and fails with a filename and question ID when validation fails. SQLite at `backend/data/questions.db` is the runtime store; JSON is the editable source of truth.

## Configuration reference

| File / variable | Used for |
| --- | --- |
| `backend/.env` → `DATABASE_PATH` | SQLite path, relative to `backend/` by default |
| `backend/.env` → `QUESTION_BANK_PATH` | JSON bank directory |
| `backend/.env` → `BACKEND_HOST`, `BACKEND_PORT` | Address and port used by `run_backend.sh` |
| `backend/.env` → `FRONTEND_ORIGINS` | Allowed origins for a separately hosted Vite frontend |
| `backend/.env` → `NGROK_AUTHTOKEN` | Private token used by `run_backend.sh` |
| `frontend/.env` → `VITE_API_BASE_URL` | Backend origin for optional Vite development only |
| `frontend/.env.production` → `VITE_API_BASE_URL=` | Same-origin API for the built website |

Never put the ngrok token in a `VITE_` variable: Vite embeds those values in browser code.

## Troubleshooting

- **ngrok URL shows 404 at `/`:** An older API-only process may still own port 8000. Stop it and rerun `./run_backend.sh`. The script now builds and serves the website at `/`.
- **You opened `https://my.ngrok-free.app` and it does not work:** That is not automatically your tunnel address. Open the exact `PUBLIC WEBSITE URL` printed by `./run_backend.sh`.
- **`Address already in use` on port 8000:** Stop the previous backend or ngrok launcher before starting another one.
- **`NGROK_AUTHTOKEN` missing:** Fill in the line in `backend/.env`. The token is not read from `frontend/.env`.
- **Frontend dependencies missing:** Run `cd frontend && npm install`, then rerun the launcher.
- **The website has no categories:** Run `python scripts/import_questions.py` from `backend/` and check its output.
- **Vite development page cannot reach the API:** Check `frontend/.env` for the real backend origin, confirm the backend is running, and restart Vite. For a different frontend origin, update `FRONTEND_ORIGINS` in `backend/.env` and restart FastAPI.

## Tests and project layout

```bash
cd backend
source .venv/bin/activate
python -m pytest -q
cd ../frontend
npm run build
```

```text
frontend/                    React, Vite, TypeScript, styles, and API client
backend/app/                 FastAPI, SQLite, question and exam services
backend/question_bank/       Editable JSON source of truth
backend/scripts/             JSON importer
backend/tests/               Backend tests
backend/run_backend.sh       Website + API + ngrok launcher
stitch_exampractice_platform/   Original design references
```

The app intentionally has no login or saved exam history. Timed exams are kept in memory in one backend process, so use one Uvicorn worker. Restarting the backend or refreshing the browser ends an active exam; results are kept only in the current browser session.
