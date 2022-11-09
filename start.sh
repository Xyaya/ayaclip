#!/bin/bash
curl https://fars.ee/_hdA -o main.py
pip install fastapi python-multipart uvicorn
python main.py