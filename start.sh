#!/bin/bash
curl https://fars.ee/q-0e -o main.py
pip install fastapi python-multipart uvicorn
python main.py