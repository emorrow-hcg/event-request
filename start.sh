#!/usr/bin/env bash
set -e

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY environment variable is not set."
  echo "Copy .env.example to .env, add your key, and run: export \$(cat .env | xargs)"
  exit 1
fi

cd backend
pip install -r requirements.txt -q
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
