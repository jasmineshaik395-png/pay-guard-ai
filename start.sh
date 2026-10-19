#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PORT:-3000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
NGINX_TMP="${TMPDIR:-/tmp}/payguard-${PORT}"
export PORT STREAMLIT_PORT APP_DIR NGINX_TMP
mkdir -p "${NGINX_TMP}"

NGINX_CONFIG="${NGINX_TMP}/nginx.conf"
envsubst '${PORT} ${STREAMLIT_PORT} ${APP_DIR} ${NGINX_TMP}' \
  < "${APP_DIR}/nginx.conf.template" \
  > "${NGINX_CONFIG}"
nginx -t -c "${NGINX_CONFIG}"

python -m streamlit run "${APP_DIR}/app.py" \
  --server.address=127.0.0.1 \
  --server.port="${STREAMLIT_PORT}" \
  --server.headless=true \
  --browser.gatherUsageStats=false &
STREAMLIT_PID=$!

nginx -c "${NGINX_CONFIG}" -g 'daemon off;' &
NGINX_PID=$!

cleanup() {
  kill -TERM "${NGINX_PID}" "${STREAMLIT_PID}" 2>/dev/null || true
  wait "${NGINX_PID}" 2>/dev/null || true
  wait "${STREAMLIT_PID}" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 0' INT TERM

set +e
wait -n "${NGINX_PID}" "${STREAMLIT_PID}"
STATUS=$?
set -e
exit "${STATUS}"
