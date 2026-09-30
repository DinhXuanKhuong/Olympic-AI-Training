#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=$(command -v python3)
elif command -v python >/dev/null 2>&1; then
  PYTHON=$(command -v python)
else
  echo "Python is required." >&2
  exit 1
fi
if ! command -v ngrok >/dev/null 2>&1; then
  echo "ngrok is required. Install the ngrok agent before running this script." >&2
  exit 1
fi
if ! "$PYTHON" -c 'import uvicorn, fastapi' 2>/dev/null; then
  echo "Backend dependencies are missing. Run: $PYTHON -m pip install -r requirements.txt" >&2
  exit 1
fi

set -a
if [[ -f .env ]]; then source .env; fi
set +a
if [[ -z "${NGROK_AUTHTOKEN:-}" ]]; then
  echo "Set NGROK_AUTHTOKEN in backend/.env before running this script." >&2
  exit 1
fi
HOST=${BACKEND_HOST:-0.0.0.0}
PORT=${BACKEND_PORT:-8000}
if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to build the frontend. Install Node.js and npm." >&2
  exit 1
fi
if [[ ! -d ../frontend/node_modules ]]; then
  echo "Frontend dependencies are missing. Run: cd frontend && npm install" >&2
  exit 1
fi
echo "Building frontend for the public website..."
(cd ../frontend && VITE_API_BASE_URL= npm run build)
NGROK_LOG=$(mktemp)
UVICORN_PID=
NGROK_PID=
cleanup() {
  trap - EXIT INT TERM
  [[ -z "$NGROK_PID" ]] || kill "$NGROK_PID" 2>/dev/null || true
  [[ -z "$UVICORN_PID" ]] || kill "$UVICORN_PID" 2>/dev/null || true
  [[ -z "$NGROK_PID" ]] || wait "$NGROK_PID" 2>/dev/null || true
  [[ -z "$UVICORN_PID" ]] || wait "$UVICORN_PID" 2>/dev/null || true
  rm -f "$NGROK_LOG"
}
trap cleanup EXIT INT TERM

echo "Starting FastAPI..."
READY=0
"$PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT" &
UVICORN_PID=$!
for _ in {1..30}; do
  if "$PYTHON" - "$PORT" <<'PY' >/dev/null 2>&1
import sys, urllib.request
for path in ("/api/health", "/"):
    urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[1]}{path}", timeout=1)
PY
  then READY=1; break; fi
  if ! kill -0 "$UVICORN_PID" 2>/dev/null; then echo "FastAPI exited unexpectedly." >&2; exit 1; fi
  sleep 1
done
if [[ "$READY" -ne 1 ]]; then echo "FastAPI did not become healthy on port $PORT." >&2; exit 1; fi
echo "Website and API running on: http://localhost:$PORT/"
echo "Starting ngrok..."
ngrok http "$PORT" --log=stdout >"$NGROK_LOG" 2>&1 &
NGROK_PID=$!
PUBLIC_URL=
for _ in {1..30}; do
  PUBLIC_URL=$("$PYTHON" - <<'PY' 2>/dev/null || true
import json, urllib.request
data=json.load(urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels', timeout=1))
print(next((item['public_url'] for item in data.get('tunnels', []) if item.get('public_url', '').startswith('https://')), ''))
PY
)
  [[ -z "$PUBLIC_URL" ]] || break
  if ! kill -0 "$NGROK_PID" 2>/dev/null; then cat "$NGROK_LOG" >&2; exit 1; fi
  sleep 1
done
if [[ -z "$PUBLIC_URL" ]]; then
  echo "ngrok did not provide a public URL. Recent output:" >&2
  tail -20 "$NGROK_LOG" >&2
  exit 1
fi
printf '\n==============================================\nPUBLIC WEBSITE URL\n%s/\n==============================================\nAPI: %s/api\nSwagger: %s/docs\n\n' "$PUBLIC_URL" "$PUBLIC_URL" "$PUBLIC_URL"
wait "$UVICORN_PID"
