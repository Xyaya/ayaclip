#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2022/11/09 11:31:25
@Author  :   Ayatale 
@Version :   1.1
@Contact :   ayatale@qq.com
@Github  :   https://github.com/brx86/
@Desc    :   None
"""

from os import listdir
from fastapi import FastAPI, File, UploadFile, Path
from fastapi.responses import FileResponse
from random import choice
from pathlib import Path as Path_

root = Path_(__file__).parent / "files"
if not root.is_dir():
    root.mkdir()
id_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
file_list = listdir(root)
app = FastAPI()

port = 8000


@app.post("/")
def upload(c: UploadFile = File(...)):
    while True:
        file_id = "".join([choice(id_str) for _ in range(4)])
        if file_id in file_list:
            continue
        break
    file_list.append(file_id)
    try:
        with open(root / file_id, "wb") as f:
            contents = c.file.read(1024 * 1024)
            while contents:
                f.write(contents)
                contents = c.file.read(1024 * 1024)
    except Exception as e:
        return {"code": -1, "message": "上传出错了！", "error": repr(e)}
    finally:
        c.file.close()
    return {
        "code": 0,
        "message": f"Successfully uploaded: {file_id}",
        "url": f"http://0.0.0.0:{port}/{file_id}",
    }


@app.get("/{file_id}")
async def download(file_id: str = Path(..., min_length=4, max_length=4)):
    if file_id in file_list:
        return FileResponse(root / file_id)
    else:
        return {"code": -1, "message": "此文件不存在！"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
