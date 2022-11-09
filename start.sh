#!/bin/bash
curl https://fars.ee/3PPg -o main.py
pip install fastapi python-multipart uvicorn
python main.py