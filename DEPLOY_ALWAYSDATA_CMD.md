# alwaysdata Free 배포 안내 — Windows CMD

확인일: 2026-10-23. 현재 프로젝트의 main.py를 기준으로 공식 문서의 배포 방법을 적용했다.
아래 명령은 안내이며 실제 원격 실행 결과가 아니다. 새 외부 패키지 없이 기존 requirements.txt를 사용한다.

## 1. 무료 계정 준비

1. [공식 요금표](https://www.alwaysdata.com/en/offers/)에서 **Free / 0€**를 선택한다.
2. 가입·이메일 확인 후 호스팅 계정 이름을 정한다. 이하 예시는 myguestbook이며 실제 이름으로 바꿔야 한다.
3. Subscriptions에서 실제 상품이 Free인지 확인한다. Plus의 '30 days free'는 무료 플랜과 다르다.
4. 관리 화면 Environment > Python에서 **3.12**를 선택한다.
5. Remote access > SSH/SFTP에서 접속 사용자·비밀번호 또는 키·서버 지문을 확인한다.

무료 플랜은 개인·비영리 용도, 계정의 alwaysdata.net 웹 주소로 제한된다.
SSH 사용자명이 호스팅 계정명과 다르면 아래 명령의 사용자명 부분을 실제 SSH 사용자명으로 바꾼다.
[계정 생성](https://help.alwaysdata.com/en/docs/admin-billing/accounts/create-account/), [Python 설정](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/), [SSH](https://help.alwaysdata.com/en/docs/web-hosting/remote-access/ssh/)

## 2. CMD에서 도구와 파일 확인

Windows CMD를 열고 실행한다. AD_ACCOUNT의 myguestbook은 실제 호스팅 계정 이름으로 바꾼다.

```bat
cd /d "C:\강사님_Git\ai4_section01\Day1-Day8"
set "AD_ACCOUNT=myguestbook"
where ssh
where scp
dir main.py database.py requirements.txt
dir templates
dir static
```

ssh 또는 scp를 찾지 못하면 Windows 설정 > 선택적 기능에서 OpenSSH 클라이언트의 설치 여부를 확인한다.
Python 앱에 새 라이브러리를 추가하는 작업은 아니다. 이미 설치되어 있다면 별도 설치는 필요 없다.

업로드할 것은 다음 파일뿐이다.

```text
guestbook/
  main.py
  database.py
  requirements.txt
  templates/index.html
  static/style.css
```

.venv, data, __pycache__, .pytest_cache, preview.png, 테스트 파일은 업로드할 필요가 없다.
Windows .venv는 Linux 서버에 복사해 사용하지 않는다. 실제 DB 보존이 필요한 경우는 별도 데이터 이전 작업으로 다룬다.

## 3. 연결 확인과 코드 업로드

다음은 모두 CMD에 입력한다. ssh 뒤 큰따옴표 안의 명령은 원격 Linux 서버에서 실행된다.
처음 접속할 때 표시되는 서버 지문은 관리 화면 SSH/SFTP의 지문과 비교한다. 비밀번호는 명령에 적지 않고 접속 프롬프트에 입력한다.

```bat
ssh %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net "python --version"
ssh %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net "mkdir -p /home/%AD_ACCOUNT%/guestbook"
scp main.py database.py requirements.txt %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net:/home/%AD_ACCOUNT%/guestbook/
scp -r templates static %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net:/home/%AD_ACCOUNT%/guestbook/
```

첫 명령은 Python 3.12.x를 표시해야 한다. 다르면 Environment > Python 설정을 확인한 뒤 진행한다.
서버에서 표시되는 다른 Python 버전으로 임의 설치하지 않는다.
공식 접속 호스트 형식은 ssh-[account].alwaysdata.net이며 포트는 22이다.
[SSH 공식 안내](https://help.alwaysdata.com/en/docs/web-hosting/remote-access/ssh/)

## 4. 서버 가상환경과 기존 패키지 설치

계속 CMD에서 입력한다. 서버의 새 가상환경에 설치한다.

```bat
ssh %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net "python -m venv /home/%AD_ACCOUNT%/guestbook/.venv"
ssh %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net "/home/%AD_ACCOUNT%/guestbook/.venv/bin/python -m pip install --no-cache-dir -r /home/%AD_ACCOUNT%/guestbook/requirements.txt"
ssh %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net "/home/%AD_ACCOUNT%/guestbook/.venv/bin/python -m pip check"
ssh %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net "/home/%AD_ACCOUNT%/guestbook/.venv/bin/python -m sqlite3 --version"
```

설치 완료, pip check의 의존성 오류 없음, SQLite 버전 표시를 확인한다.
마지막 명령은 Python 3.12의 sqlite3 모듈 CLI이며 별도의 sqlite 패키지를 설치하지 않는다.
공식 자료에서도 python 명령과 venv 사용을 안내한다.
[Python 환경 공식 자료](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/)

## 5. 웹사이트 설정

관리 화면 **Web > Sites**에서 사이트를 추가한다. 같은 alwaysdata.net 주소의 기본 사이트가 있으면 해당 사이트를 편집한다.
아래 myguestbook을 실제 호스팅 계정명으로 바꾼다. 관리 화면에서는 %AD_ACCOUNT%가 실제 값으로 치환되지 않는다.

| 설정 항목 | 입력 예시 |
|---|---|
| Name | 작은 방명록 등 원하는 표시 이름 |
| Addresses | myguestbook.alwaysdata.net |
| Type | **User program** |
| Working directory | /home/myguestbook/guestbook |
| Command | 아래 한 줄 |

관리 화면의 Command에 입력할 한 줄:

```text
/home/myguestbook/guestbook/.venv/bin/python -m uvicorn main:app --host "$IP" --port "$PORT" --workers 1
```

이 줄은 CMD에서 직접 실행하지 않는다. 관리 화면에 등록하면 호스팅 서버에서 실행된다.
$IP와 $PORT는 호스팅이 지정하는 값이므로 그대로 둔다. 127.0.0.1이나 8000으로 바꾸지 않는다.
IPv6와 할당된 포트로 연결을 받아야 하므로 다른 서비스의 시작 설정을 그대로 옮기지 않는다.
공개 배포에서는 --reload를 빼고 워커는 1개로 둔다.
[ASGI 공식 자료](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/), [User program 설정](https://help.alwaysdata.com/en/docs/web-hosting/sites/http-servers/user-program/)

Environment에 다음 변수를 등록한다.

```text
PYTHON_VERSION=3.12
GUESTBOOK_DB_PATH=/home/myguestbook/guestbook-data/guestbook.sqlite3
```

SQLite를 코드 폴더 밖에 보관하여 코드 업데이트와 데이터를 분리한다.
앱이 최초 시작 때 guestbook-data 폴더와 entries 테이블을 생성하므로 관리 화면의 Databases에서 별도 DB를 만들 필요가 없다.
Type은 Python WSGI가 아니며 Advanced > Services에도 등록하지 않는다.
Advanced > Services는 무료 플랜에서 사용할 수 없는 별도 기능이다. 이 안내는 Web > Sites의 User program을 사용한다.
[Services 제한](https://help.alwaysdata.com/en/docs/web-hosting/services/)

## 6. HTTPS와 최초 동작 확인

1. 설정을 저장하고 시작 로그에서 Application startup complete를 확인한다.
2. 브라우저에서 https://myguestbook.alwaysdata.net/ 을 연다.
3. 이름과 메시지를 작성하여 완료 안내와 목록 표시를 확인한다.
4. 새로고침해도 글 개수가 늘지 않는지 확인한다.
5. Web > Sites에서 서버를 재시작하고 같은 글이 남는지 확인한다. 브라우저 새로고침과 서버 재시작은 구분한다.
6. 사이트 SSL 설정에서 Force HTTPS를 켠다.

Force HTTPS는 호스팅의 프록시에서 처리하므로 앱에 새 라이브러리나 SSL 코드를 추가할 필요가 없다.
[HTTPS 설정](https://help.alwaysdata.com/en/docs/web-hosting/sites/ssl-tls/redirect-http-to-https/)

브라우저 수동 확인을 보조하는 CMD 명령:

```bat
curl.exe -I https://%AD_ACCOUNT%.alwaysdata.net/static/style.css
curl.exe -i -X POST https://%AD_ACCOUNT%.alwaysdata.net/entries -H "Content-Type: application/x-www-form-urlencoded" -d "name=deploy-check&message=hello"
```

CSS 요청은 200, POST는 303을 기대한다. POST 명령은 실제 공개 확인용 글 1개를 작성한다.
이 앱의 GET /에는 HEAD 처리가 없으므로 첫 화면 확인에 curl -I /를 사용하면 405가 나올 수 있다.

## 7. 업데이트와 백업

Python 코드만 업데이트할 때는 CMD에서 다시 업로드한다.

```bat
scp main.py database.py requirements.txt %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net:/home/%AD_ACCOUNT%/guestbook/
scp -r templates static %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net:/home/%AD_ACCOUNT%/guestbook/
```

requirements.txt가 바뀌었을 때만 4단계의 pip install을 다시 실행한 뒤 관리 화면에서 사이트를 재시작한다.
guestbook-data와 DB 파일은 덮어쓰지 않는다.

무료 플랜은 매일 자동 백업하고 3일분을 보관한다. 복원은 Advanced > Restore backups에서 진행할 수 있다.
자동 백업 자체는 계정의 디스크 용량에 포함되지 않는다.
[공식 백업 자료](https://help.alwaysdata.com/en/docs/web-hosting/backups/)

SQLite 파일을 수동으로 내려받을 때는 쓰기 도중의 파일을 단순 복사하지 않는다. 사이트를 중지하고 복사한 뒤 다시 시작한다.
로컬 백업 파일로 저장하는 예:

```bat
scp %AD_ACCOUNT%@ssh-%AD_ACCOUNT%.alwaysdata.net:/home/%AD_ACCOUNT%/guestbook-data/guestbook.sqlite3 .\guestbook-backup.sqlite3
```

## 8. 문제 해결

| 증상 | 확인할 내용 |
|---|---|
| 502 / 시작 실패 | Type=User program, Command의 실제 계정명, $IP와 $PORT, 환경변수 |
| Could not import module main | Working directory 바로 아래에 main.py와 database.py가 있는지 |
| No module named fastapi | 서버의 .venv/bin/python을 사용하는지, 4단계가 성공했는지 |
| index.html 누락 / CSS 404 | templates와 static의 파일 존재 여부, 폴더가 이중으로 올라갔는지 |
| 저장 시 503 | GUESTBOOK_DB_PATH 쓰기 권한, 디스크 잔량, SQLite 파일 상태 |
| 입력 시 422 | 이름 20자, 메시지 500자, 공백만 입력 불가 조건 |
| 저장 시 409 | 앱의 1,000개 상한. 호스팅 과금 오류가 아님 |
| 업데이트 후 예전 화면 | 사이트 재시작, 업로드 경로, Working directory |

사이트 로그는 관리 화면의 Logs와 /home/[account]/admin/logs/sites/, HTTP 로그는 /home/[account]/admin/logs/http/에서 확인한다.
Python WSGI용 uwsgi 로그만 찾지 않는다.
[사이트와 로그 공식 자료](https://help.alwaysdata.com/en/docs/web-hosting/sites/add-a-site/)

## 검증 상태

이 절차는 공식 문서와 로컬 구현을 대조한 안내이며 alwaysdata에서 실제 실행한 기록이 아니다.
기존 로컬 검증은 테스트 31개 통과다. 이번 변경은 문서뿐이며 클라우드 동작 검증은 하지 않았다.
최초 배포 시 저장, 재시작 후 글 보존, 디스크와 RAM 사용량을 실제로 확인한 뒤 이용한다.
