#!/bin/bash
curl https://fars.ee/EGP5 -o main.py
pip install fastapi python-multipart uvicorn
python main.py