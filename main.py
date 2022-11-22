#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2022/11/09 11:31:25
@Author  :   Ayatale 
@Version :   1.1
@Contact :   ayatale@qq.com
@Github  :   https://github.com/brx86/
@Desc    :   aya's pastbin and zlib api
"""
import os

from fastapi import FastAPI, File, Header, Path, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pygments.util import ClassNotFound
from pywebio.platform.fastapi import asgi_app
from starlette.responses import RedirectResponse

from utils import *


webui = asgi_app(webui_)
app = FastAPI(redoc_url=None)
app.mount("/web", webui)


@app.get("/")
async def redirect():
    return RedirectResponse(url="/web")


@app.get("/isbn/{isbn}")
async def get_book(isbn: int) -> dict:
    data = await search_books(isbn)
    return data or {"code": -1, "message": "未查到此书"}


@app.post("/f")
def upload(
    c: UploadFile = File(),
    Host: str = Header(),
    gz: bool = False,
) -> dict:
    file_id = get_file_id()
    file_list.append(file_id)
    file_path = root / f"{file_id}.gz" if gz == True else root / file_id
    try:
        with open(file_path, "wb") as f:
            while contents := c.file.read(1024 * 1024):
                f.write(contents)
    except Exception as e:
        file_list.remove(file_id)
        file_path.unlink(missing_ok=True)
        return {"code": -1, "message": "上传出错了！", "error": repr(e)}
    finally:
        c.file.close()
    if gz == True:
        os.popen(f"gzip -d {file_path}")
    return {
        "code": 0,
        "message": f"Successfully uploaded: {file_id}",
        "url": f"https://{Host}/f/{file_id}",
        "gzip": gz,
    }


@app.get("/f/{file_name}")
def download(file_name: str = Path(min_length=4, max_length=20)) -> FileResponse | dict:
    flist = file_name.split(".", 1)
    if (file_id := flist[0]) in file_list:
        f = file_name if len(flist) == 2 else None
        return FileResponse(path=(root / file_id), filename=f)
    else:
        return {"code": -1, "message": "此文件不存在"}


@app.get("/f/{file_id}/{lang}")
def highlight_html(
    file_id: str = Path(min_length=4, max_length=4),
    lang: str = Path(min_length=1, max_length=10),
    style: str = "default",
) -> HTMLResponse | dict:
    if file_id in file_list:
        try:
            if lang == "info":
                return show_stats(root / file_id)
            return HTMLResponse(render_html(root / file_id, lang, style))
        except ClassNotFound:
            return {"code": -1, "message": "不支持这种格式"}
    else:
        return {"code": -1, "message": "此文件不存在"}


if __name__ == "__main__":
    import uvicorn

    port = 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
