#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ -f "${ROOT_DIR}/.env.production" ]] || { printf 'Create .env.production from .env.production.example first.\n' >&2; exit 1; }
"${ROOT_DIR}/deploy/deploy.sh"
