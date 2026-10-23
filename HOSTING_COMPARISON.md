# 무료 호스팅 비교와 추천

검색·확인 기준일: 2026-10-23, 한국 시간. 공식 요금·기술 문서를 기준으로 비교했다.
이전 DEPLOYMENT.md에서 다룬 두 서비스 외에 후보를 넓혀 확인한 결과이다.

## 비교 기준

현재 앱은 Python 3.12 + FastAPI + SQLite 파일 + HTML/CSS이다.
웹 서버 실행, 재시작 후 DB 파일 유지, 추가 기술 최소화, 무료 이용 지속 가능성 순서로 평가했다.
아래 추천은 공식 문서를 바탕으로 한 적합성 판단이며 해당 계정에 실제 배포하여 검증한 결과는 아니다.

| 서비스 | 현 무료 범위 | FastAPI / SQLite 보존 | 장점 | 단점 | 판단 |
|---|---|---|---|---|---|
| **alwaysdata Free** | 1GB 디스크, RAM 256MB, CPU 1/4, 3일분 백업 | ASGI를 Web > Sites의 User program으로 실행. 계정 파일 공간에 DB 저장하는 구성 | 기존 Python·SQLite 구조 유지, Docker·외부 DB 불필요, SSH 제공 | 개인·비영리 용도만, 제공 alwaysdata.net 주소만 사용, 자원 작음. 서버 설정 필요 | **이 학습용 방명록의 1순위**. 파일 보존·쓰기·재시작은 최초 배포 후 실제 확인 필요. [요금](https://www.alwaysdata.com/en/offers/), [제한](https://help.alwaysdata.com/en/docs/admin-billing/billing/public-cloud-prices/), [ASGI](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/) |
| **Railway Free** | 30일/$5 체험 후 매월 $1 크레딧, 서비스당 최대 0.5GB RAM, 0.5GB 볼륨 | FastAPI 실행 및 영속 볼륨 구성 가능. DB 경로를 볼륨에 지정해야 함 | SQLite 유지 가능, Git 배포와 관리 편리 | 무료는 소액 크레딧 한도 내 사용. DB뿐 아니라 메모리·CPU·통신·볼륨 비용도 고려해야 해 상시 무료 가동을 단정할 수 없음 | 차선. 소규모·간헐 시연에 검토. [요금](https://railway.com/pricing) |
| **Render Free** | 월 750시간/워크스페이스. 무료 서버 제공 | FastAPI 지원. 무료 인스턴스의 로컬 SQLite는 재배포·재시작·비활성 중지 시 소실 | 배포 절차가 쉽고 FastAPI 공식 가이드 있음 | 15분 비활성 후 중지, 무료 영속 디스크 없음 | 글이 사라져도 되는 시연용. 보존 목적 방명록에는 부적합. [무료 정책](https://render.com/docs/free) |
| **Koyeb Free** | 조직당 무료 웹 서비스 1개, 512MB RAM, 0.1 vCPU, 로컬 SSD 2GB | FastAPI 지원. 무료 인스턴스에 영속 볼륨 연결 불가 | 작은 앱 실행과 Git 배포에 편리 | 2GB 로컬 디스크를 영속 DB 공간으로 간주하면 안 됨 | 현재 SQLite 보존 조건에는 부적합. [무료 범위](https://www.koyeb.com/docs/faqs/pricing), [볼륨 제한](https://www.koyeb.com/docs/reference/volumes) |
| **PythonAnywhere Free** | 512MiB 디스크, 웹 앱 1개·워커 1개·1개월 만료 | SQLite 사용 가능. FastAPI용 ASGI는 실험 기능이고 장기 요금 미확정 | Python 중심 환경, 파일형 DB 사용 가능 | 일반 WSGI 설정으로 FastAPI를 실행할 수 없음. 계정의 ASGI 이용 가능 여부 확인 필요 | 조건부 후보. [무료 범위](https://help.pythonanywhere.com/pages/FreeAccountsFeatures/), [ASGI](https://help.pythonanywhere.com/pages/ASGICommandLine/), [SQLite](https://help.pythonanywhere.com/pages/KindsOfDatabases) |
| **Hugging Face Spaces** | 정적 Spaces는 무료. 현재 새 Docker/Gradio compute Space 생성은 유료 플랜 필요 | 현재 앱은 서버가 필요하므로 정적 Space로 배포 불가 | 데모 공유와 Docker 앱 기능 제공 | 과거의 무료 CPU 문구만 보고 새 Docker Space까지 무료라고 판단하면 안 됨 | **현재 신규 무료 후보에서 제외**. [현재 생성 정책](https://huggingface.co/docs/hub/en/spaces-overview) |

## 추천 근거

**개인·비영리 학습 프로젝트라는 현재 조건에서는 alwaysdata Free를 추천한다.**
FastAPI를 User program 웹사이트로 실행하고, SQLite 파일을 계정 홈 디렉터리에 보관하는 방식이다.
별도 DB 서비스·프레임워크 변경·컨테이너 구성이 필요 없어 Codex.md의 기술 최소화 조건과 잘 맞는다.

공식 요금표에 명시된 현재 무료 용량은 1GB이다. 과거 100MB 안내와 혼동하지 않는다.
무료는 개인·비영리 용도이며 사이트 주소는 계정의 alwaysdata.net 주소로 제한된다.
상업 서비스로 바뀌면 이 추천의 무료 이용 전제도 바뀐다. [공식 제한](https://help.alwaysdata.com/en/docs/admin-billing/billing/public-cloud-prices/)

무료 플랜에서 금지된 Advanced > Services는 백그라운드 서비스 기능이다.
이 앱은 Web > Sites > User program을 사용한다. 두 메뉴를 혼동하지 않는다.
[웹 프로그램](https://help.alwaysdata.com/en/docs/web-hosting/sites/http-servers/user-program/), [별도 Services 기능](https://help.alwaysdata.com/en/docs/web-hosting/services/)

1GB는 DB 전용이 아니라 코드·Python 환경·기타 계정 파일을 포함한 공간이다.
앱 데이터가 작아도 로그와 패키지 공간을 함께 확인해야 한다. 256MB RAM 적합성은 첫 배포 후 실제 사용량으로 확인한다.
공식 문서의 Python 지원·파일 저장 공간을 근거로 SQLite 사용 가능성을 판단했으며, 해당 호스팅의 SQLite 파일 잠금과 재시작 보존은 아직 원격 검증하지 않았다.

## 다음 단계

실제 배포 절차는 [alwaysdata CMD 배포 안내](DEPLOY_ALWAYSDATA_CMD.md)에 정리했다.
이번 작업은 조사와 문서 작성이다. 계정 가입, 업로드, 배포, 요금제 변경은 실행하지 않았다.
