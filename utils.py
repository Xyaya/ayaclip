import json
import os
import re
from pathlib import Path as Path_
from random import choice
from string import ascii_letters
from time import gmtime, strftime

import httpx
from lxml import etree
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pywebio import config
from pywebio.output import (
    put_button,
    put_buttons,
    put_link,
    put_markdown,
    put_table,
    put_tabs,
    toast,
)
from pywebio.pin import pin, put_textarea, pin_update
from pywebio.session import run_js

root = Path_(__file__).parent / "files"
if not root.is_dir():
    root.mkdir()
file_list = os.listdir(root)


with open(Path_(__file__).parent / "README.md", "r") as f:
    readme = f.read()


def get_file_id() -> str:
    while (file_id := "".join([choice(ascii_letters) for _ in range(4)])) in file_list:
        pass
    return file_id


def format_size(size: float) -> str:
    size_text = ("B", "KB", "MB", "GB")
    index = (len(str(size)) - 1) // 3
    return f"{size/(1024**(index)):.1f}{size_text[index]}"


def show_stats(path: Path_) -> dict:
    stat = path.stat()
    ftime_8 = strftime("%Y-%m-%d %H:%M:%S", gmtime(stat.st_mtime + 28800))
    return {
        "size": (stat.st_size, format_size(stat.st_size)),
        "mtime": (stat.st_mtime, ftime_8),
    }


def render_html(path: Path_, lang: str, style: str) -> str:
    if path.stat().st_size > 1000000:
        return "文本超过1M，不再渲染"
    with open(path, "r") as f:
        code = f.read()
    lexer = get_lexer_by_name(lang)
    formatter = HtmlFormatter(linenos=True, style=style)
    css = (
        formatter.get_style_defs(".highlight")
        + "pre {padding: 6px;font-size: 14px;line-height: 1.5;}"
    )
    return f'<style type="text/css">{css}</style>{highlight(code, lexer, formatter)}'


async def search_books(isbn: int) -> dict | None:
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        r = await client.get(f"https://annas-archive.org/isbn/{isbn}")
        pattern = re.compile(r'href="/md5/(\w+)"')
        md5_list = pattern.findall(r.text)
        if md5_list:
            book_md5 = md5_list[0]
        else:
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


def btn_copy(text):
    js = (
        "var aux = document.createElement('input');"
        f"aux.setAttribute('value', '{text}');"
        "document.body.appendChild(aux);"
        "aux.select();document.execCommand('copy');"
        "document.body.removeChild(aux)"
    )
    run_js(js)
    toast(f"{text} 复制成功！", color="#4eb7cd")


@config(title="AyaClip", theme="minty")
def webui_():
    def btn_upload(text):
        file_id = get_file_id()
        try:
            with open(root / file_id, "w") as f:
                f.write(text)  # type: ignore
            file_list.append(file_id)
            stat = show_stats(root / file_id)
            url = f"https://clip.ay1.us/f/{file_id}"
            # url = f"http://127.0.0.1:7777/f/{file_id}"
            put_table(
                [
                    [
                        stat["mtime"][1],
                        stat["size"][1],
                    ],
                    [
                        put_link(url, url=url),
                        put_button("复制", onclick=lambda: btn_copy(url)),
                    ],
                ]
            )
        except Exception as e:
            (root / file_id).unlink(missing_ok=True)
            toast(f"{e!r}", color="error")

    put_tabs(
        [
            {
                "title": "AyaClip",
                "content": [
                    put_textarea("AyaClip", rows=20, code={"lineWrapping": False}),
                    put_buttons(
                        [
                            {"label": "上传", "value": "submit", "color": "primary"},
                            {"label": "清除", "value": "reset", "color": "warning"},
                        ],
                        onclick=[
                            lambda: btn_upload(pin.AyaClip),
                            lambda: pin_update("AyaClip", value=""),
                        ],
                    ),
                ],
            },
            {"title": "使用说明", "content": put_markdown(readme)},
        ]
    )
