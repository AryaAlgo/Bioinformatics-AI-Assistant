#!/bin/bash

set -e

cd "$(dirname "$0")"

if ! command -v ollama >/dev/null 2>&1; then
    echo "Error: Ollama is not installed."
    exit 1
fi

if ! ollama list | grep -q "qwen-coder"; then
    echo "Error: Ollama model 'qwen-coder' is not installed."
    echo "Please configure the model as described in README.md."
    exit 1
fi

if [ ! -f "app/local_ai_chat_v3_fixed.py" ]; then
    echo "Error: Application file not found."
    exit 1
fi

if [ ! -x "bioenv/bin/python" ]; then
    echo "Error: Python environment not found."
    echo "Create the environment and install requirements first."
    exit 1
fi

exec bioenv/bin/python app/local_ai_chat_v3_fixed.py
