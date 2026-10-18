# AI 티스토리 자동 블로그 포스팅 프로젝트 (열려있는 크롬 연동 방식)

매일 지정된 시간에 AI(OpenAI GPT)를 활용하여 흥미로운 주제의 글과 이미지를 자동으로 생성하고, **현재 로그인되어 열려있는 크롬 브라우저를 직접 원격 제어**하여 티스토리(`jeces.tistory.com`)에 자동으로 포스팅하는 파이썬 프로그램입니다.

> 💡 **특징**: 카카오/티스토리 봇 감지 및 로그인 제한을 우회하기 위해, **사용자가 이미 로그인해 놓은 크롬 브라우저**에 연결하여 포스팅을 진행합니다!

---

## 📁 프로젝트 구조

```text
.
├── .github/
│   └── workflows/
│       └── daily_post.yml   # GitHub Actions 매일 자동 실행
├── run_auto_blogger.bat     # Windows 실행용 스크립트
├── start_chrome_debug.bat   # 크롬 디버깅 모드 실행용 스크립트 (최초 1회 실행)
├── config.py                # 환경 변수 및 설정 관리
├── content_generator.py     # 파워블로거 스타일 AI 글 & 이미지 생성 모듈
├── tistory_browser.py       # 크롬 브라우저 원격 연동 (CDP) 및 포스팅 모듈
├── main.py                  # 실행 메인 스크립트
├── requirements.txt         # 필요 의존성 패키지
├── .env.example             # 환경변수 샘플
└── tests/
    └── test_auto_blogger.py # 유닛 테스트
```

---

## 🚀 사용 방법 (가장 쉬운 2단계!)

### 1단계: 디버깅 크롬 켜고 티스토리 로그인하기 (최초 1회)
1. 모든 크롬 창을 닫습니다.
2. `start_chrome_debug.bat` 파일(또는 명령 프롬프트)을 실행하여 **디버깅 크롬**을 엽니다.
   - 명령 프롬프트(CMD)에서 직접 실행할 경우:
     ```cmd
     "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
     ```
3. 열린 크롬 창에서 [티스토리](https://www.tistory.com) 접속 ➔ **카카오계정으로 미리 로그인해 둡니다.**

### 2단계: 자동 포스터 실행하기
- `.env.example` 파일의 이름을 `.env`로 변경합니다. (티스토리 블로그 이름 `jeces` 입력)
- `run_auto_blogger.bat` 파일을 더블 클릭하면 열려있는 크롬 창을 그대로 원격 제어하여 블로그 포스팅이 자동으로 완료됩니다! 🎉

---

## ❓ 질문 & 해결책

- **왜 크롬을 디버깅 모드로 켜나요?**
  - 티스토리가 봇(자동화) 로그인을 강력히 차단하기 때문에, 사람이 직접 로그인해 둔 실제 크롬 창을 제어하는 방식이 가장 안전하고 확실합니다.
