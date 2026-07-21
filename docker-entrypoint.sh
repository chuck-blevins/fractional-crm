#!/bin/sh
# Nexlayer (and most orchestrators) mount the persistent /data volume owned by
# root, which shadows the image-time chown. Fix ownership at startup, then drop
# to the non-root app user so the FastAPI process never runs as root.
set -e
DB_DIR="$(dirname "${CRM_DB_PATH:-/data/crm.db}")"
mkdir -p "$DB_DIR"
chown -R appuser:appuser "$DB_DIR"
exec gosu appuser "$@"
