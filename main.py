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
import json
import os
import re
from functools import partial
from pathlib import Path as Path_
from random import choice
from string import ascii_letters

import httpx
from fastapi import FastAPI, File, Header, Path, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from lxml import etree
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from pywebio import config as pywebio_config
from pywebio.input import textarea
from pywebio.output import put_button, put_markdown, put_table, toast
from pywebio.platform.fastapi import asgi_app
from pywebio.session import run_js
from starlette.responses import RedirectResponse

root = Path_(__file__).parent / "files"
if not root.is_dir():
    root.mkdir()
file_list = os.listdir(root)
app = FastAPI(redoc_url=None)

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0"
}

with open(Path_(__file__).parent / "README.md", "r") as f:
    readme = f.read()


@pywebio_config(theme="minty")
def enterpoint_():
    put_markdown(readme)


@pywebio_config(theme="minty")
def webui_():
    def btn_copy(text):
        js = (
            "var aux = document.createElement('input');"
            f"aux.setAttribute('value', '{text}');"
            "document.body.appendChild(aux);"
            "aux.select();document.execCommand('copy');"
            "document.body.removeChild(aux)"
        )
        run_js(js)
        toast("复制成功！", color="#4eb7cd")

    text = textarea("AyaClip", rows=20, code={"lineWrapping": False})
    while (file_id := "".join([choice(ascii_letters) for _ in range(4)])) in file_list:
        continue
    try:
        with open(root / file_id, "w") as f:
            f.write(text)  # type: ignore
        file_list.append(file_id)
        url = f"https://clip.ay1.us/f/{file_id}"
        # url = f"http://127.0.0.1:7777/f/{file_id}"
        put_markdown("## AyaClip")
        put_table(
            [
                [
                    put_markdown(url),
                    put_button("复制", onclick=partial(btn_copy, text=url)),
                ],
            ]
        )
        put_markdown(f"```\n{text}\n```")
    except Exception as e:
        (root / file_id).unlink(missing_ok=True)
        toast(f"{e!r}", color="error")


async def search_books(isbn: int) -> dict | None:
    async with httpx.AsyncClient(headers=headers) as client:
        r = await client.get(f"https://annas-archive.org/isbn/{isbn}")
        pattern = re.compile(r'href="/md5/(\w+)"')
        md5_list = pattern.findall(r.text)
        if md5_list:
            book_md5 = md5_list[0]
        else:
            # return r.text
            return None
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


def render_html(path: Path_, h: str, style: str) -> str:
    if path.stat().st_size > 1000000:
        return "文本超过1M，不再渲染"
    with open(path, "r") as f:
        code = f.read()
    lexer = get_lexer_by_name(h)
    formatter = HtmlFormatter(linenos=True, style=style)
    css = (
        formatter.get_style_defs(".highlight")
        + "pre {padding: 6px;font-size: 14px;line-height: 1.5;}"
    )
    return f'<style type="text/css">{css}</style>{highlight(code, lexer, formatter)}'


@app.get("/isbn/{isbn}")
async def get_book(isbn: int) -> dict:
    data = await search_books(isbn)
    return data or {"code": -1, "message": "未查到此书"}


webui = asgi_app(webui_)
enterpoint = asgi_app(enterpoint_)
app.mount("/web", webui)
app.mount("/readme", enterpoint)


@app.get("/")
async def redirect():
    return RedirectResponse(url="/readme")


@app.post("/f")
def upload(
    c: UploadFile = File(),
    Host: str = Header(),
    gz: bool = False,
) -> dict:
    while (file_id := "".join([choice(ascii_letters) for _ in range(4)])) in file_list:
        continue
    file_path = root / f"{file_id}.gz" if gz == True else root / file_id
    try:
        with open(file_path, "wb") as f:
            while contents := c.file.read(1024 * 1024):
                f.write(contents)
        file_list.append(file_id)
    except Exception as e:
        file_path.unlink(missing_ok=True)
        return {"code": -1, "message": "上传出错了！", "error": repr(e)}
    finally:
        c.file.close()
    if gz == True:
        os.system(f"gzip -d {file_path}")
    return {
        "code": 0,
        "message": f"Successfully uploaded: {file_id}",
        "url": f"https://{Host}/f/{file_id}",
        "gzip": gz,
    }


@app.get("/f/{file_id}")
def download(file_id: str = Path(min_length=4, max_length=4)) -> FileResponse | dict:
    if file_id in file_list:
        return FileResponse(root / file_id)
    else:
        return {"code": -1, "message": "此文件不存在"}


@app.get("/f/{file_id}/{h}")
def highlight_html(
    file_id: str = Path(min_length=4, max_length=4),
    h: str = Path(default="text"),
    style: str = "default",
) -> HTMLResponse | dict:
    if file_id in file_list:
        try:
            return HTMLResponse(render_html(root / file_id, h, style))
        except ClassNotFound:
            return {"code": -1, "message": "不支持这种格式"}
    else:
        return {"code": -1, "message": "此文件不存在"}


if __name__ == "__main__":
    import uvicorn

    port = 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
