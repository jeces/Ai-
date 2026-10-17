# AI 티스토리 자동 블로그 포스팅 프로젝트

매일 지정된 시간에 AI(OpenAI GPT)를 활용하여 흥미로운 주제의 글을 자동으로 생성하고, 티스토리(Tistory) 블로그에 자동으로 포스팅하는 파이썬 프로그램입니다.

GitHub Actions를 활용하여 서버 없이도 매일 무료로 자동 실행할 수 있습니다.

---

## 📁 프로젝트 구조

```text
.
├── .github/
│   └── workflows/
│       └── daily_post.yml   # 매일 자동 실행을 위한 GitHub Actions 워크플로우
├── config.py                # 환경 변수 및 설정 관리
├── content_generator.py     # OpenAI API / 템플릿 기반 블로그 글 생성 모듈
├── tistory_api.py           # 티스토리 Open API 글쓰기 연동 모듈
├── main.py                  # 실행 메인 스크립트
├── requirements.txt         # 필요 의존성 패키지
├── .env.example             # 로컬 실행용 환경변수 샘플
└── tests/
    └── test_auto_blogger.py # 유닛 테스트
```

---

## ⚙️ 사전 준비사항 (발급 방법)

### 1. 티스토리 Open API Access Token 발급받기
1. [티스토리 Open API 가이드](https://tistory.github.io/tistory-openapi-blog/) 접속 및 오픈 API 오픈 등록
2. Open API 오픈 등록 시:
   - **서비스명**: 티스토리 자동 포스터 (자율)
   - **서비스 URL**: `http://localhost` (또는 본인 블로그 주소)
   - **Callback URL**: `http://localhost`
3. 등록 완료 후 **App ID (Client ID)** 및 **Secret Key**를 확인합니다.
4. 웹 브라우저 주소창에 아래 URL을 입력하여 인증 코드(code)를 받습니다:
   ```text
   https://www.tistory.com/oauth/authorize?client_id={YOUR_CLIENT_ID}&redirect_uri=http://localhost&response_type=code
   ```
5. 브라우저 주소창의 `http://localhost/?code={YOUR_CODE}...` 에서 `code` 값을 복사합니다.
6. 아래 요청을 보내 Access Token을 발급받습니다 (curl 또는 브라우저 이용):
   ```text
   https://www.tistory.com/oauth/access_token?client_id={YOUR_CLIENT_ID}&client_secret={YOUR_CLIENT_SECRET}&redirect_uri=http://localhost&code={YOUR_CODE}&grant_type=authorization_code
   ```
7. 응답받은 `access_token` 값을 복사해 둡니다.

### 2. OpenAI API Key 발급받기 (선택 사항)
- [OpenAI API Platform](https://platform.openai.com/)에 접속하여 API Key를 발급받습니다.
- API Key가 없어도 기본 템플릿 기반으로 포스팅이 정상 동작합니다.

---

## 🚀 로컬 실행 방법

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경변수 설정**
   `.env.example` 파일의 이름을 `.env`로 변경하거나 복사한 뒤, 발급받은 정보를 입력합니다.
   ```env
   TISTORY_ACCESS_TOKEN=발급받은_티스토리_엑세스_토큰
   TISTORY_BLOG_NAME=본인의_블로그_식별_이름 (예: https://abc.tistory.com 이면 abc)
   OPENAI_API_KEY=발급받은_OpenAI_API_키
   ```

3. **프로그램 실행**
   ```bash
   python main.py
   ```

4. **테스트 실행**
   ```bash
   PYTHONPATH=. pytest
   ```

---

## ⏰ GitHub Actions로 매일 자동 작성 설정하기

이 저장소를 GitHub에 올린 후, GitHub Secrets를 등록하면 매일 정해진 시간(기본값: 한국시간 오전 9시)에 자동으로 글이 생성되어 포스팅됩니다.

1. GitHub 저장소의 **Settings** -> **Secrets and variables** -> **Actions** 이동
2. **New repository secret** 버튼을 클릭하여 아래 환경 변수들을 등록합니다:
   - `TISTORY_ACCESS_TOKEN`: 티스토리 엑세스 토큰 (필수)
   - `TISTORY_BLOG_NAME`: 티스토리 블로그 이름 (필수)
   - `OPENAI_API_KEY`: OpenAI API Key (선택)
   - `TISTORY_CATEGORY_ID`: 카테고리 ID (선택, 기본값: `0`)
   - `TISTORY_VISIBILITY`: 발행 여부 (선택, `3`: 공개 발행, `0`: 비공개, 기본값: `3`)
3. 등록 완료 후 **Actions** 탭에서 **Daily Tistory Auto Post** 워크플로우의 **Run workflow**를 눌러 즉시 테스트할 수 있습니다.
