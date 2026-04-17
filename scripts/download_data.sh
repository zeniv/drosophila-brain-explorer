#!/usr/bin/env bash
# Скрипт для скачивания данных коннектома с Edmond MPG
# DOI: 10.17617/3.CZODIW
# Paper: https://www.nature.com/articles/s41586-024-07763-9

set -e

DATA_DIR="$(dirname "$0")/../data"
mkdir -p "$DATA_DIR"

echo "=== Drosophila Brain Model — Download Data ==="
echo "Source: https://edmond.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.CZODIW"
echo ""
echo "Please download the following files manually from Edmond MPG:"
echo "  1. connections.parquet  → data/connections.parquet"
echo "  2. completeness.csv     → data/completeness.csv"
echo ""
echo "Or clone the original model and copy data:"
echo "  git clone https://github.com/philshiu/Drosophila_brain_model /tmp/dro_model"
echo "  cp /tmp/dro_model/data/* $DATA_DIR/"
echo ""
echo "After downloading, run:"
echo "  docker compose up --build"
