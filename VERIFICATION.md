# 실제 검증 기록

실행일: 2026-10-23, Asia/Seoul.

## 환경

- Python 3.12.14. Codex 번들 Python 3.12로 만든 임시 가상환경을 사용했다.
- FastAPI 0.115.12, Pydantic 2.11.5, Uvicorn 0.34.2, httpx 0.28.1, pytest 8.3.5.
- 기존 상위 .venv는 사용하지 않았다. 테스트용 환경에 위 패키지들이 이미 준비되어 있어 이번 작업에서 새 패키지를 설치하지 않았다.
- 실행 위치: C:\강사님_Git\ai4_section01\Day1-Day8.

## 실제 테스트 명령과 결과

```powershell
& "$env:TEMP/fastapi-lesson04-contract312/Scripts/python.exe" -m pytest -q test_guestbook.py
```

실제 결과: **31 passed, 1 warning in 1.21s**, 종료 코드 0.
warning은 Starlette TestClient에서 사용하는 AnyIO BlockingPortal 별칭의 DeprecationWarning이다.
이것은 테스트 실패가 아니며, 새 버전으로 바꾸기 위해 수업의 지정 패키지를 임의 변경하지 않았다.

| 검사 범위 | 확인한 동작 |
|---|---|
| 기본 화면 | 빈 목록, 폼, CSS 정상 응답, JavaScript 없음 |
| 작성 | 폼 제출 → 303 → 200 목록, 새로고침 후 중복 없음 |
| 허용 경계 | 이름 1·20자, 메시지 1·500자 |
| 정규화 | 앞뒤 공백 제거, 메시지 안 줄바꿈 보존 |
| 잘못된 입력 | 필수값 누락, 빈 문자열, 공백만 입력, 길이 초과, NUL, 추가 필드 거부 |
| 요청 형식 | 중복 필드·잘못된 UTF-8·잘못된 폼 422, JSON 415, 큰 본문 413 |
| 출력과 저장 | HTML 태그 이스케이프, SQL 구문을 메시지 텍스트로 보존 |
| 오류 화면 | 입력 재표시에서도 HTML 속성·태그 이스케이프 |
| 목록 | 11개 작성 후 첫 페이지 10개·두 번째 1개, 최신순, 빈 페이지 |
| 페이지 입력 | 0, -1, 101, abc에 422 |
| 보존·테이블 | 같은 SQLite 파일로 앱을 다시 열어 글 보존, entries 테이블 하나, 외래키 없음 |
| 상한·경쟁 | 999개 상태에서 동시 쓰기 2개 중 1개만 성공, 1,000개 유지, 추가 POST 409 |
| DB 오류 | 503 응답, 내부 경로 노출 없음 |
| 브라우저 헤더 | nosniff, 동일 출처 폼 정책 |

## 실제 서버와 브라우저 확인

테스트 데이터가 기본 guestbook.sqlite3와 섞이지 않게 미리보기용 DB 경로를 별도로 지정했다.

```powershell
$env:GUESTBOOK_DB_PATH = 'C:/강사님_Git/ai4_section01/Day1-Day8/data/preview.sqlite3'
& "$env:TEMP/fastapi-lesson04-contract312/Scripts/python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8765 --workers 1
```

실제 서버 로그와 브라우저에서 확인한 흐름:

1. GET / → 200, GET /static/style.css → 200.
2. 이름 '첫 방문자', 메시지 '배운 Python으로 만든 첫 방명록이에요.\n들러 주셔서 반갑습니다!'를 입력했다.
3. POST /entries → 303, GET /?saved=true → 200.
4. 완료 안내, 총 1개, 이름·한국 시간·두 줄 메시지 표시를 확인했다.
5. 브라우저 새로고침 후에도 총 1개와 같은 메시지가 유지됐다.

작성 완료 화면은 preview.png에 저장했다. 브라우저 확인 뒤 미리보기 서버를 종료했다.
data/preview.sqlite3는 로컬 확인용 데이터이며 .gitignore로 배포 소스에서 제외된다.
기본 실행은 data/guestbook.sqlite3를 새로 생성하므로 이 확인용 글을 포함하지 않는다.

## 확인 한계와 범위

- 로컬 서버와 실제 브라우저 화면을 확인했다. 휴대폰 실기기·모든 브라우저 조합은 확인하지 않았다.
- 좁은 화면에서는 세로 배치를 적용하는 CSS가 있다. 별도 모바일 실기기 테스트 결과로 주장하지 않는다.
- 수업 폴더의 전체 .py 구문 분석은 실행했으나 수업 전체 프로그램을 실행한 것은 아니다.
- 무료 배포 정책은 공식 문서를 확인했다. 사용자 선택에 따라 계정·호스팅을 만들거나 실제 공개 배포하지 않았다.
- 영속 로컬 파일에서 보존 검사는 통과했지만 Render 무료 파일시스템의 소실 제약을 해결한 것은 아니다.
- 부하 테스트, 운영 스팸 관리, 사용자 인증, 수정·삭제 기능은 이번 구현 범위에 없다.
- Codex.md 및 기존 Day1~Day8 수업 소스는 변경하지 않았다.
