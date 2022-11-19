#!/bin/bash
curl https://raw.githubusercontent.com/Xyaya/ayaclip/main/main.py -o main.py
pip install fastapi python-multipart uvicorn
python main.py