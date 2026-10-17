# AI 티스토리 자동 블로그 포스팅 프로젝트

매일 지정된 시간에 AI(OpenAI GPT)를 활용하여 흥미로운 주제의 글을 자동으로 생성하고, 티스토리(Tistory) 블로그에 자동으로 포스팅하는 파이썬 프로그램입니다.

**Windows 데스크톱 환경** 및 **GitHub Actions (무료 자동 실행)**을 모두 지원합니다.

---

## 📁 프로젝트 구조

```text
.
├── .github/
│   └── workflows/
│       └── daily_post.yml   # GitHub Actions 매일 자동 실행
├── run_auto_blogger.bat     # Windows 데스크톱 더블클릭 실행/스케줄러용 파일
├── config.py                # 환경 변수 및 설정 관리
├── content_generator.py     # OpenAI API / 템플릿 기반 블로그 글 생성 모듈
├── tistory_api.py           # 티스토리 Open API 글쓰기 연동 모듈
├── main.py                  # 실행 메인 스크립트
├── requirements.txt         # 필요 의존성 패키지
├── .env.example             # 환경변수 샘플
└── tests/
    └── test_auto_blogger.py # 유닛 테스트
```

---

## ⚙️ 사전 준비사항 (발급 방법)

### 1. 티스토리 Open API Access Token 발급받기
1. [티스토리 Open API 가이드](https://tistory.github.io/tistory-openapi-blog/) 접속 및 오픈 API 등록
2. Open API 오픈 등록 시 입력 사항:
   - **서비스명**: 티스토리 자동 포스터
   - **서비스 URL**: `http://localhost`
   - **Callback URL**: `http://localhost`
3. 등록 완료 후 **App ID (Client ID)** 및 **Secret Key**를 확인합니다.
4. 웹 브라우저 주소창에 아래 URL을 입력하여 인증 코드를 받습니다 (`{YOUR_CLIENT_ID}` 부분 변경):
   ```text
   https://www.tistory.com/oauth/authorize?client_id={YOUR_CLIENT_ID}&redirect_uri=http://localhost&response_type=code
   ```
5. 브라우저 주소창의 `http://localhost/?code={YOUR_CODE}...` 에서 `code` 값(문자열)을 복사합니다.
6. 아래 요청을 웹 브라우저 주소창이나 curl에 입력하여 Access Token을 발급받습니다:
   ```text
   https://www.tistory.com/oauth/access_token?client_id={YOUR_CLIENT_ID}&client_secret={YOUR_CLIENT_SECRET}&redirect_uri=http://localhost&code={YOUR_CODE}&grant_type=authorization_code
   ```
7. 화면에 표시된 `access_token` 값(문자열)을 복사합니다.

### 2. OpenAI API Key 발급받기 (선택 사항)
- [OpenAI API Platform](https://platform.openai.com/)에 접속하여 API Key를 발급받습니다.
- API Key를 넣으면 GPT가 글을 작성해주며, 없더라도 내장된 포스팅 템플릿으로 정상 동작합니다.

---

## 💻 Windows 데스크톱에서 실행하는 방법

### 1. 환경 설정
1. 이 프로젝트의 압축을 풀거나 폴더를 다운로드합니다.
2. `.env.example` 파일의 이름을 `.env`로 변경합니다. (또는 메모장으로 `.env` 파일 새로 생성)
3. 메모장이나 에디터로 `.env` 파일을 열고 발급받은 값을 입력한 뒤 저장합니다:
   ```env
   TISTORY_ACCESS_TOKEN=발급받은_티스토리_엑세스_토큰
   TISTORY_BLOG_NAME=본인_블로그_이름 (예: abc.tistory.com 이면 abc)
   OPENAI_API_KEY=발급받은_OpenAI_API_키
   ```

### 2. 실행 방법
- **더블 클릭 실행**: `run_auto_blogger.bat` 파일을 더블 클릭하면 자동으로 필요한 라이브러리가 설치되고 블로그 글이 즉시 작성됩니다.
- **명령 프롬프트(CMD) 실행**:
  ```cmd
  pip install -r requirements.txt
  python main.py
  ```

---

## ⏰ Windows 작업 스케줄러로 매일 자동 실행하기 (로컬 PC)

컴퓨터가 켜져 있을 때 매일 정해진 시간에 자동으로 글을 올리려면 Windows 작업 스케줄러를 등록하세요.

1. Windows 검색창에 **작업 스케줄러 (Task Scheduler)** 입력 후 실행
2. 우측 메뉴에서 **작업 만들기... (Create Task)** 클릭
3. **일반 (General)** 탭:
   - 이름: `티스토리 자동 포스팅` 입력
4. **트리거 (Triggers)** 탭 -> **새로 만들기**:
   - 작업 시작: `일정에 따라` -> `매일` 설정 및 원하는 시간 지정 (예: 매일 오전 09:00)
5. **동작 (Actions)** 탭 -> **새로 만들기**:
   - 동작: `프로그램 시작`
   - 프로그램/스크립트: `run_auto_blogger.bat` 파일의 전체 경로 선택 (예: `C:\Users\Username\tistory-auto-blogger\run_auto_blogger.bat`)
   - 시작 위치(옵션): 프로젝트 폴더 경로 입력 (예: `C:\Users\Username\tistory-auto-blogger\`)
6. **확인** 버튼을 눌러 저장합니다.

---

## ☁️ GitHub Actions로 PC가 꺼져도 매일 무료로 자동 실행하기

컴퓨터를 켜놓지 않아도 매일 자동으로 글을 작성하도록 하려면 GitHub Actions를 사용할 수 있습니다.

1. 이 저장소를 본인의 GitHub 계정으로 올려줍니다 (Fork 또는 Push).
2. GitHub 저장소의 **Settings** -> **Secrets and variables** -> **Actions** 이동
3. **New repository secret** 버튼을 눌러 시크릿 값을 등록합니다:
   - `TISTORY_ACCESS_TOKEN`: 티스토리 엑세스 토큰
   - `TISTORY_BLOG_NAME`: 블로그 이름
   - `OPENAI_API_KEY`: OpenAI API 키 (선택)
4. 설정이 완료되면 매일 한국시간 오전 9시에 자동으로 글이 작성됩니다.
