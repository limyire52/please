"""실제 임시 SQLite 파일로 폼·검증·보존·저장 상한을 검사한다."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from html.parser import HTMLParser
import sqlite3

from fastapi.testclient import TestClient
import pytest

from database import GuestbookFull, GuestbookStore, MAX_ENTRIES
from main import create_app


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "guestbook.sqlite3"


@pytest.fixture
def client(db_path):
    with TestClient(create_app(db_path)) as session:
        yield session


def post_entry(client, name="방문자", message="반갑습니다", **kwargs):
    return client.post("/entries", data={"name": name, "message": message}, **kwargs)


class EntriesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.in_message = False

    def handle_starttag(self, tag, attrs):
        if tag == "p" and ("class", "message") in attrs:
            self.in_message = True

    def handle_endtag(self, tag):
        if tag == "p":
            self.in_message = False

    def handle_data(self, data):
        if self.in_message:
            self.messages.append(data)


def messages(response):
    parser = EntriesParser()
    parser.feed(response.text)
    return parser.messages


def test_empty_page_and_static_css(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "아직 남겨진 인사가 없어요" in response.text
    assert 'method="post"' in response.text
    assert "<script" not in response.text
    assert client.get("/static/style.css").status_code == 200


def test_post_redirect_get_and_refresh(client):
    response = post_entry(client, follow_redirects=False)
    assert response.status_code == 303
    page = client.get(response.headers["location"])
    assert page.status_code == 200
    assert "인사가 남겨졌어요" in page.text
    assert messages(page) == ["반갑습니다"]
    assert messages(client.get("/")) == ["반갑습니다"]


@pytest.mark.parametrize("name,message", [("가", "나"), ("가" * 20, "나" * 500)])
def test_allowed_length_endpoints(client, name, message):
    response = post_entry(client, name, message)
    assert response.status_code == 200
    assert messages(response) == [message]


def test_strip_and_keep_line_breaks(client):
    response = post_entry(client, "  방문자  ", "  첫째 줄\n둘째 줄  ")
    assert "<strong>방문자</strong>" in response.text
    assert messages(response) == ["첫째 줄\n둘째 줄"]


@pytest.mark.parametrize("body", [
    {}, {"name": "가"}, {"message": "나"},
    {"name": "", "message": "나"}, {"name": "가", "message": ""},
    {"name": "  ", "message": "나"}, {"name": "가", "message": " \n\t "},
    {"name": "가" * 21, "message": "나"}, {"name": "가", "message": "나" * 501},
    {"name": "가", "message": "a\x00b"},
    {"name": "가", "message": "나", "admin": "true"},
])
def test_invalid_form_keeps_state(client, body):
    post_entry(client, message="기존 글")
    response = client.post(
        "/entries", data=body,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert messages(client.get("/")) == ["기존 글"]


@pytest.mark.parametrize("body", ["name=a&name=b", "name=%FF&message=a", "not-a-form"])
def test_malformed_form(client, body):
    response = client.post(
        "/entries", content=body,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 422
    assert messages(client.get("/")) == []


def test_unsupported_content_type_and_body_limit(client):
    assert client.post("/entries", json={"name": "가", "message": "나"}).status_code == 415
    response = client.post(
        "/entries", content="name=a&message=" + "x" * 8192,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 413
    assert messages(client.get("/")) == []


def test_html_and_sql_are_stored_as_text(client, db_path):
    message = "<script>alert('x')</script>\n'; DROP TABLE entries;--"
    response = post_entry(client, name='<b>이름</b>', message=message)
    assert "<script>alert" not in response.text
    assert "&lt;script&gt;" in response.text
    assert "&lt;b&gt;이름&lt;/b&gt;" in response.text
    assert messages(response) == [message]
    with closing(sqlite3.connect(db_path)) as connection:
        assert connection.execute("SELECT message FROM entries").fetchone()[0] == message


def test_invalid_form_escapes_preserved_values(client):
    response = post_entry(client, name='" autofocus onfocus="x', message="</textarea><script>x</script>")
    assert response.status_code == 422
    assert "</textarea><script>" not in response.text
    assert "&quot; autofocus" in response.text


def test_order_and_pagination(client):
    for number in range(11):
        post_entry(client, message=f"글 {number}")
    assert messages(client.get("/")) == [f"글 {number}" for number in range(10, 0, -1)]
    assert messages(client.get("/?page=2")) == ["글 0"]
    assert messages(client.get("/?page=3")) == []


@pytest.mark.parametrize("page", ["0", "-1", "101", "abc"])
def test_invalid_page(client, page):
    assert client.get(f"/?page={page}").status_code == 422


def test_persists_across_app_restart_and_has_one_table(db_path):
    with TestClient(create_app(db_path)) as first:
        post_entry(first, message="다시 시작해도 남는 글")
    with TestClient(create_app(db_path)) as second:
        assert messages(second.get("/")) == ["다시 시작해도 남는 글"]
    with closing(sqlite3.connect(db_path)) as connection:
        tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        assert tables == [("entries",)]
        assert connection.execute("PRAGMA foreign_key_list(entries)").fetchall() == []


def test_capacity_is_atomic_and_returns_409(client, db_path):
    with closing(sqlite3.connect(db_path)) as connection, connection:
        connection.executemany(
            "INSERT INTO entries (name, message, created_at) VALUES (?, ?, ?)",
            [("가", "기존 글", "2026-10-23T00:00:00+00:00")] * (MAX_ENTRIES - 1),
        )
    store = GuestbookStore(db_path)

    def add_one(number):
        try:
            store.add("방문자", f"동시 글 {number}")
            return "created"
        except GuestbookFull:
            return "full"

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert sorted(executor.map(add_one, [1, 2])) == ["created", "full"]
    assert post_entry(client).status_code == 409
    assert store.list_page(1)[1] == MAX_ENTRIES


def test_database_failure_returns_503_without_details(client, monkeypatch):
    def unavailable(page):
        raise sqlite3.OperationalError("private filesystem path")

    monkeypatch.setattr(client.app.state.store, "list_page", unavailable)
    response = client.get("/")
    assert response.status_code == 503
    assert "private filesystem path" not in response.text


def test_browser_security_headers(client):
    response = client.get("/")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "form-action 'self'" in response.headers["content-security-policy"]
