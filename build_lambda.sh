#!/usr/bin/env bash
set -euo pipefail

echo "[*] Cleaning old build..."
rm -rf lambda_package
mkdir -p lambda_package

echo "[*] Installing dependencies into lambda_package/..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements/chat_service.txt -t lambda_package/

echo "[*] Copying application code..."
cp -r api lambda_package/api
cp -r app lambda_package/app
cp local_content.json lambda_package/local_content.json

echo "[*] Done."
