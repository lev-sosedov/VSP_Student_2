#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.production"
BACKUP_DIR="${BACKUP_DIR:-/opt/vsp/backups}"
[[ -f "${ENV_FILE}" ]] || { printf 'missing %s\n' "${ENV_FILE}" >&2; exit 1; }
set -a
source "${ENV_FILE}"
set +a
mkdir -p "${BACKUP_DIR}"
chmod 700 "${BACKUP_DIR}"
STAMP="$(date -u +%Y%m%d_%H%M%S)"
TARGET="${BACKUP_DIR}/postgres_${STAMP}.sql"
docker compose --env-file "${ENV_FILE}" -f "${ROOT_DIR}/docker-compose.prod.yml" exec -T postgres pg_dumpall -U "${POSTGRES_USER:?POSTGRES_USER required}" > "${TARGET}"
chmod 600 "${TARGET}"
if [[ ! -s "${TARGET}" ]]; then
  rm -f "${TARGET}"
  printf 'Backup is empty\n' >&2
  exit 1
fi
printf 'PostgreSQL backup created: %s (%s bytes)\n' "${TARGET}" "$(stat -c '%s' "${TARGET}")"
