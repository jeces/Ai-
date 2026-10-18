# AI 티스토리 자동 블로그 포스팅 프로젝트 (웹 브라우저 원격 제어 방식)

매일 지정된 시간에 AI(OpenAI GPT)를 활용하여 흥미로운 주제의 글과 이미지를 자동으로 생성하고, **Playwright 브라우저 자동화**를 사용하여 티스토리(Tistory) 블로그(`jeces.tistory.com`)에 자동으로 포스팅하는 파이썬 프로그램입니다.

---

## 📁 프로젝트 구조

```text
.
├── .github/
│   └── workflows/
│       └── daily_post.yml   # GitHub Actions 매일 자동 실행
├── run_auto_blogger.bat     # Windows 데스크톱 더블클릭 실행/스케줄러용 파일
├── config.py                # 환경 변수 및 설정 관리
├── content_generator.py     # 파워블로거 스타일 AI 글 & 이미지 생성 모듈
├── tistory_browser.py       # Playwright 브라우저 로그인 및 자동 포스팅 모듈
├── main.py                  # 실행 메인 스크립트
├── requirements.txt         # 필요 의존성 패키지
├── .env.example             # 환경변수 샘플
└── tests/
    └── test_auto_blogger.py # 유닛 테스트
```

---

## 💻 Windows 데스크톱에서 실행하는 방법

### 1. 환경 설정 및 .env 파일 생성
1. 이 프로젝트의 폴더를 다운로드합니다.
2. `.env.example` 파일의 이름을 `.env`로 변경합니다. (또는 새 텍스트 문서를 만들어 `.env`로 저장)
3. 메모장으로 `.env` 파일을 열고 로그인 정보와 블로그 이름을 입력합니다:
   ```env
   TISTORY_LOGIN_ID=본인_카카오_또는_티스토리_계정_아이디
   TISTORY_LOGIN_PW=본인_비밀번호
   TISTORY_BLOG_NAME=jeces
   OPENAI_API_KEY=발급받은_OpenAI_API_키 (선택)
   HEADLESS=False
   ```
   > 💡 **Tip**: `HEADLESS=False`로 설정하면 브라우저가 직접 켜져서 로그인하고 글 쓰는 과정을 눈으로 확인할 수 있습니다!

### 2. 실행 방법
- **더블 클릭 실행**: `run_auto_blogger.bat` 파일을 더블 클릭합니다.
  - 자동으로 필요한 패키지와 크롬 브라우저가 설치되며 실행 결과가 화면에 유지됩니다.

---

## ❓ Windows 실행 시 문제가 발생할 때 (Troubleshooting)

1. **더블클릭해도 창이 그냥 켜졌다 꺼지는 경우**
   - **원인**: 컴퓨터에 파이썬(Python)이 설치되어 있지 않거나 환경변수(PATH) 설정이 안 되어 있는 경우입니다.
   - **해결책**: [python.org](https://www.python.org/downloads/)에서 Python 3.10 이상을 설치할 때 **`Add Python to PATH`** 옵션을 꼭 체크해 주세요!

2. **`필수 환경변수가 설정되지 않았습니다` 오류가 나오는 경우**
   - **해결책**: 프로젝트 폴더 안에 `.env` 파일이 존재하는지, `TISTORY_LOGIN_ID`와 `TISTORY_LOGIN_PW`가 제대로 작성되어 있는지 확인해 주세요.

---

## ⏰ Windows 작업 스케줄러로 매일 자동 실행하기 (로컬 PC)

1. Windows 검색창에 **작업 스케줄러 (Task Scheduler)** 입력 후 실행
2. 우측 메뉴에서 **작업 만들기... (Create Task)** 클릭
3. **일반 (General)** 탭:
   - 이름: `티스토리 자동 포스팅` 입력
4. **트리거 (Triggers)** 탭 -> **새로 만들기**:
   - 작업 시작: `일정에 따라` -> `매일` 설정 및 원하는 시간 지정 (예: 매일 오전 09:00)
5. **동작 (Actions)** 탭 -> **새로 만들기**:
   - 동작: `프로그램 시작`
   - 프로그램/스크립트: `run_auto_blogger.bat` 파일의 전체 경로 지정
   - 시작 위치: 프로젝트 폴더 경로 지정

---

## ☁️ GitHub Actions로 PC가 꺼져도 매일 무료로 자동 실행하기

1. 이 저장소를 본인의 GitHub 계정에 올립니다.
2. GitHub 저장소의 **Settings** -> **Secrets and variables** -> **Actions** 이동
3. **New repository secret** 버튼을 눌러 시크릿 값을 등록합니다:
   - `TISTORY_LOGIN_ID`: 티스토리/카카오 계정 아이디
   - `TISTORY_LOGIN_PW`: 티스토리/카카오 계정 비밀번호
   - `TISTORY_BLOG_NAME`: `jeces`
   - `OPENAI_API_KEY`: OpenAI API 키 (선택)
4. 매일 한국시간 오전 9시에 자동으로 브라우저가 동작하여 글을 작성해 줍니다.
