#!/usr/bin/env bash
# Levanta la base de datos y el PMV automáticamente al abrir el Codespace.
set -e
cd "$(dirname "$0")/.."

echo "Esperando a que Docker esté listo..."
for i in $(seq 1 60); do
  if docker info >/dev/null 2>&1; then break; fi
  sleep 2
done

echo "Levantando MySQL y Streamlit con Docker Compose..."
docker compose up --build -d

echo "Listo. El PMV queda en el puerto 8501 (pestaña Ports)."
echo "Usuarios de prueba: admin / 1234  y  operador / 1234"
