#!/bin/bash
# post-bootstrap.sh — Patroni post_bootstrap hook
# Runs on the primary after the cluster is first initialised.
set -e

echo "==> Creating smart_catalog database..."
psql -U postgres -c "CREATE DATABASE smart_catalog;" 2>/dev/null || true

echo "==> Running init-db.sql..."
psql -U postgres -d smart_catalog -f /docker-entrypoint-initdb.d/init-db.sql

echo "==> Post-bootstrap complete."
