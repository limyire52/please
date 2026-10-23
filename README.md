# 작은 방명록

Day1~Day8에서 배운 Python·FastAPI를 사용한 HTML 중심 방명록입니다.
이 폴더의 Codex.md를 기준으로 구현했습니다. Python 3.12, SQLite 테이블 하나, 기본 HTML 폼과 CSS로 구성하며 새 외부 라이브러리는 추가하지 않았습니다.

## 기능과 계약

- 이름 1~20자, 메시지 1~500자. 앞뒤 공백을 제거한 뒤 검사하고 공백뿐인 값은 거부합니다.
- 글을 작성하고 최신순으로 읽습니다. 페이지당 10개, 최대 100페이지입니다.
- 모든 글은 공개됩니다. 이름과 메시지 이외의 개인정보는 수집하지 않습니다.
- 전체 1,000개에 도달하면 기존 글을 유지하고 새 작성을 거부합니다.
- UTC로 저장하고 화면에서는 한국 시간으로 표시합니다.

| 요청 | 상태 | 동작 |
|---|---|---|
| GET / | 200 | 작성 폼과 최신 글 목록 |
| GET /?page=2 | 200 | 두 번째 목록. 비어 있어도 200 |
| GET /?page=0 또는 101 또는 abc | 422 | 유효하지 않은 페이지 |
| POST /entries | 303 | 정상 저장 후 GET /?saved=true#entries로 이동 |
| POST /entries 입력 누락·공백·길이 초과·중복/추가 필드·잘못된 폼 | 422 | 오류를 HTML로 표시, 저장하지 않음 |
| POST /entries 본문 8 KiB 초과 | 413 | 저장하지 않음 |
| POST /entries 폼 이외의 Content-Type | 415 | 저장하지 않음 |
| POST /entries 1,000개 저장 후 추가 작성 | 409 | 기존 데이터 유지 |
| 읽기·쓰기 중 SQLite 오류 | 503 | 내부 경로·SQL 오류 내용은 표시하지 않음 |

POST는 application/x-www-form-urlencoded 형식입니다. JSON API가 아니며 Swagger UI는 사용하지 않습니다.
HTML 오류 문구와 API의 JSON 검증 오류는 별개입니다.

## 로컬 실행

이 README와 main.py가 있는 폴더에서 실행합니다. Windows CMD 예시입니다.

```bat
cd /d "C:\강사님_Git\ai4_section01\Day1-Day8"
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --workers 1
```

브라우저에서 http://127.0.0.1:8000 을 엽니다. HTML 파일을 더블 클릭하지 않습니다.
종료는 Ctrl+C입니다. 가상환경 활성화 없이 위와 같이 python.exe를 직접 실행할 수 있습니다.
py 명령이 없다면 설치된 Python 3.12 실행 파일의 절대 경로로 첫 명령을 실행합니다. 예:

```bat
"C:\Users\Playdata\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m venv .venv
```

위 절대 경로는 이번 PC에서 확인한 Codex 번들 Python 경로입니다. 다른 PC에서는 해당 PC의 설치 경로를 사용합니다.
상위 폴더의 기존 .venv는 이번 검증에 사용하지 않았습니다.

DB는 첫 서버 시작 때 data/guestbook.sqlite3로 생성됩니다. 같은 파일이 유지되는 로컬 환경에서는 재시작 후에도 글이 남습니다.
서버 작업 폴더가 바뀌어도 기본 DB 위치는 이 프로젝트의 data 폴더입니다.
다른 위치를 쓰려면 시작 전에 GUESTBOOK_DB_PATH를 지정합니다. 배포 시에는 영속 저장 경로의 절대 경로를 사용하세요.

```bat
set "GUESTBOOK_DB_PATH=C:\강사님_Git\ai4_section01\Day1-Day8\data\guestbook.sqlite3"
```

## 테스트

```bat
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q test_guestbook.py
```

테스트는 pytest의 임시 폴더에 별도 DB를 만들어 실제 방명록을 변경하지 않습니다.
다른 차시에도 main.py가 있으므로 이 폴더에서 이 테스트 파일을 지정하세요.
이번 실제 결과는 VERIFICATION.md에 기록했습니다.

## 구성과 학습 연결

| 파일 | 역할 |
|---|---|
| main.py | 폼 파싱, Pydantic 검증, HTML 출력, 요청 처리 |
| database.py | 테이블 생성, 목록 조회, 트랜잭션 저장과 상한 |
| templates/index.html | JavaScript 없는 기본 HTML 폼과 목록 틀 |
| static/style.css | 기본 화면과 좁은 화면의 세로 배치 |
| test_guestbook.py | 실제 임시 SQLite를 사용한 기능 검사 |
| ANALYSIS.md | Day1~Day8의 문법·처리 방식과 적용 근거 |
| DEPLOYMENT.md | 무료 호스팅의 조건과 배포 준비 절차 |
| HOSTING_COMPARISON.md | 최신 무료 서비스 비교와 추천 |
| DEPLOY_ALWAYSDATA_CMD.md | alwaysdata Free의 CMD 기준 배포 절차 |
| VERIFICATION.md | 실제 실행 환경·명령·결과·확인 한계 |
| preview.png | 브라우저에서 작성 완료를 확인한 화면 |

## 데이터 구조

```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 20),
    message TEXT NOT NULL CHECK(length(message) BETWEEN 1 AND 500),
    created_at TEXT NOT NULL
);
```

테이블은 entries 하나이며 외래키가 없습니다. AUTOINCREMENT를 사용하지 않아 sqlite_sequence 테이블도 생성하지 않습니다.
사용자 입력을 SQL에 문자열로 붙이지 않고 ? 매개변수에 전달합니다.
HTML 출력 시에는 이름·메시지를 이스케이프하여 태그가 실행되지 않게 합니다.

DB와 가상환경은 Git에 포함하지 않습니다. 백업은 서버를 종료한 뒤 SQLite 파일을 별도로 복사하면 됩니다.
기존 DB를 지우면 글을 되돌릴 수 없으므로 초기화 명령은 제공하지 않습니다.
