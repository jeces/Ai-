# AI 티스토리 자동 포스트 작성 프로그램

매일 지정된 시간에 AI(OpenAI GPT)를 활용하여 흥미로운 주제의 글과 이미지를 자동으로 생성하고, **브라우저를 통해 편리하게 티스토리(`jeces.tistory.com`)에 포스팅하는 파이썬 프로그램**입니다.

---

## 🚀 사용 방법 (매우 간단합니다!)

1. **`run_auto_blogger.bat` 더블 클릭 실행**
2. 화면에 **크롬 브라우저 창**이 켜지고 티스토리 로그인 화면이 나옵니다.
3. **카카오/티스토리 로그인을 직접 완료**합니다.
   - 💡 로그인 정보(쿠키)가 `./user_data` 폴더에 안전하게 자동 저장되므로, **다음 실행부터는 재로그인 없이 완전 자동으로 글이 작성됩니다!**
4. 로그인이 완료되면 프로그램이 이를 자동으로 감지하여 **제목, AI 본문, 고화질 이미지, 태그까지 입력 후 자동으로 발행**을 완료합니다!

---

## 📁 프로젝트 구조

```text
.
├── .github/
│   └── workflows/
│       └── daily_post.yml   # GitHub Actions 매일 자동 실행
├── run_auto_blogger.bat     # Windows 실행용 배치 파일
├── config.py                # 환경 변수 및 설정 관리
├── content_generator.py     # 파워블로거 스타일 AI 글 & 이미지 생성 모듈
├── tistory_browser.py       # 브라우저 로그인 감지 및 포스팅 자동화 모듈
├── main.py                  # 메인 실행 스크립트
├── requirements.txt         # 필요 의존성 패키지
└── tests/
    └── test_auto_blogger.py # 유닛 테스트
```
