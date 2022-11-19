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

import httpx, json, re
from lxml import etree
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


async def search_books(isbn):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://annas-archive.org/isbn/{isbn}")
        pattern = re.compile(r'href="/md5/(\w+)"')
        md5_list = pattern.findall(r.text)
        if md5_list:
            book_md5 = md5_list[0]
        else:
            return r.text
        book_url = f"https://annas-archive.org/md5/{book_md5}"
        r = await client.get(book_url)
        html = etree.HTML(r.text)  # type: ignore
        book_json = json.loads(html.xpath("/html/body/div[2]/div")[-1].text)
        book_info = book_json.get("file_unified_data", {})
        return {
            "cover_url": book_info.get("cover_url_best", ""),
            "title": book_info.get("title_best", ""),
            "author": book_info.get("author_best", ""),
            "publisher": book_info.get("publisher_best", ""),
            "edition": book_info.get("edition_varia_best", ""),
            "description": book_info.get("stripped_description_best", ""),
            "isbn": book_json.get("isbns_rich")[0][2],
            "size": f'{book_info.get("filesize_best",0)/1000000:.2f}M',
            "down_urls": {_[0]: _[1] for _ in book_json.get("download_urls", [])},
        }


@app.post("/f")
def upload(c: UploadFile = File(...)):
    while (file_id := "".join([choice(id_str) for _ in range(4)])) in file_list:
        continue
    file_list.append(file_id)
    try:
        with open(root / file_id, "wb") as f:
            while contents := c.file.read(1024 * 1024):
                f.write(contents)
    except Exception as e:
        return {"code": -1, "message": "上传出错了！", "error": repr(e)}
    finally:
        c.file.close()
    return {
        "code": 0,
        "message": f"Successfully uploaded: {file_id}",
        "url": f"https://ayaclip.onrender.com/f/{file_id}",
    }


@app.get("/f/{file_id}")
async def download(file_id: str = Path(..., min_length=4, max_length=4)):
    if file_id in file_list:
        return FileResponse(root / file_id)
    else:
        return {"code": -1, "message": "此文件不存在"}


@app.get("/isbn/{isbn}")
async def get_book(isbn: int):
    data = await search_books(isbn)
    return data or {"code": -1, "message": "未查到此书"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=port)
