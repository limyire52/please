"""HTML 폼과 SQLite로 만든 작은 방명록. 외부 API나 JavaScript를 쓰지 않는다."""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from html import escape
import os
from pathlib import Path
import sqlite3
from string import Template
from typing import Annotated
from urllib.parse import parse_qs

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from database import GuestbookFull, GuestbookStore, MAX_ENTRIES, PAGE_SIZE

BASE_DIR = Path(__file__).resolve().parent
MAX_BODY_BYTES = 8192
KST = timezone(timedelta(hours=9))
PAGE_TEMPLATE = Template((BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8"))


class EntryIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, strict=True)
    name: str = Field(min_length=1, max_length=20)
    message: str = Field(min_length=1, max_length=500)

    @field_validator("name", "message")
    @classmethod
    def reject_control_characters(cls, value: str):
        if any(ord(character) < 32 and character not in "\n\r\t" for character in value):
            raise ValueError("제어 문자를 입력할 수 없습니다.")
        return value


def render_page(store, page=1, *, notice="", error="", name="", message="", status=200):
    rows, total = store.list_page(page)
    cards = []
    for row in rows:
        local_time = datetime.fromisoformat(row["created_at"]).astimezone(KST)
        cards.append(
            '<li class="entry"><div class="entry-meta">'
            f'<strong>{escape(row["name"])}</strong>'
            f'<time datetime="{escape(row["created_at"], quote=True)}">'
            f'{local_time:%Y.%m.%d %H:%M} · 한국 시간</time></div>'
            f'<p class="message">{escape(row["message"])}</p></li>'
        )
    entries = "".join(cards) or '<li class="empty">아직 남겨진 인사가 없어요. 첫 인사를 남겨 주세요.</li>'
    pagination = []
    if page > 1:
        pagination.append(f'<a href="/?page={page - 1}#entries">← 이전</a>')
    pagination.append(f'<span aria-current="page">{page} 페이지</span>')
    if page * PAGE_SIZE < total:
        pagination.append(f'<a href="/?page={page + 1}#entries">다음 →</a>')
    notification = ""
    if notice:
        notification = f'<p class="notice" role="status">{escape(notice)}</p>'
    if error:
        notification = f'<p class="error" role="alert">{escape(error)}</p>'
    html = PAGE_TEMPLATE.substitute(
        entries=entries, total=total, max_entries=MAX_ENTRIES,
        pagination="".join(pagination), notification=notification,
        name=escape(name, quote=True), message=escape(message),
    )
    return HTMLResponse(html, status_code=status)


def create_app(db_path: Path | None = None):
    path = db_path if db_path is not None else Path(
        os.environ.get("GUESTBOOK_DB_PATH", str(BASE_DIR / "data" / "guestbook.sqlite3"))
    )
    store = GuestbookStore(Path(path))

    @asynccontextmanager
    async def lifespan(application):
        await asyncio.to_thread(store.initialize)
        yield

    application = FastAPI(title="작은 방명록", lifespan=lifespan, docs_url=None, redoc_url=None)
    application.state.store = store
    application.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

    @application.middleware("http")
    async def response_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; style-src 'self'; form-action 'self'; "
            "base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    @application.exception_handler(sqlite3.Error)
    async def database_error(request, error):
        return HTMLResponse(
            '<!doctype html><html lang="ko"><meta charset="utf-8">'
            '<title>잠시 후 다시 시도해 주세요</title><h1>지금은 방명록을 불러올 수 없습니다.</h1>'
            '<p>잠시 후 다시 시도해 주세요.</p><a href="/">방명록으로 돌아가기</a></html>',
            status_code=503,
        )

    @application.get("/", response_class=HTMLResponse)
    def index(page: Annotated[int, Query(ge=1, le=100)] = 1, saved: bool = False):
        return render_page(store, page, notice="인사가 남겨졌어요. 고맙습니다!" if saved else "")

    @application.post("/entries", response_class=HTMLResponse)
    async def create_entry(request: Request):
        # HTML 기본 폼을 표준 라이브러리로 읽어 python-multipart 추가 설치를 피한다.
        media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if media_type != "application/x-www-form-urlencoded":
            return await asyncio.to_thread(render_page, store, error="작성 폼으로 인사를 남겨 주세요.", status=415)

        body = bytearray()
        async for chunk in request.stream():
            if len(body) + len(chunk) > MAX_BODY_BYTES:
                return await asyncio.to_thread(render_page, store, error="요청이 너무 큽니다.", status=413)
            body.extend(chunk)

        fields = {}
        try:
            parsed = parse_qs(
                body.decode("utf-8"), keep_blank_values=True, strict_parsing=True,
                encoding="utf-8", errors="strict", max_num_fields=2,
            )
            if any(len(values) != 1 for values in parsed.values()):
                raise ValueError("중복 필드")
            fields = {key: values[0] for key, values in parsed.items()}
            entry = EntryIn.model_validate(fields)
        except (ValueError, ValidationError):
            return await asyncio.to_thread(
                render_page, store, error="이름은 1~20자, 메시지는 1~500자로 입력해 주세요. 공백만 입력할 수 없습니다.",
                name=fields.get("name", ""), message=fields.get("message", ""), status=422,
            )
        try:
            await asyncio.to_thread(store.add, entry.name, entry.message)
        except GuestbookFull:
            return await asyncio.to_thread(
                render_page, store, error="방명록이 가득 찼습니다. 지금은 새 글을 받을 수 없어요.",
                name=entry.name, message=entry.message, status=409,
            )
        # Post/Redirect/Get: 목록에서 새로고침해도 폼이 다시 제출되지 않는다.
        return RedirectResponse("/?saved=true#entries", status_code=303)

    return application


app = create_app()
