import time
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class TistoryBrowser:
    def __init__(self, login_id: str, login_pw: str, blog_name: str, headless: bool = True):
        self.login_id = login_id
        self.login_pw = login_pw
        self.blog_name = blog_name
        self.headless = headless

    def _fill_first_available(self, page, selectors: list[str], value: str, description: str) -> bool:
        """목록에 있는 셀렉터 중 첫 번째로 발견되는 입력 창에 값을 입력합니다."""
        for selector in selectors:
            try:
                el = page.query_selector(selector)
                if el and el.is_visible():
                    el.fill(value)
                    logger.info(f"{description} 입력 완료 (selector: {selector})")
                    return True
            except Exception:
                continue
        return False

    def publish_post(self, title: str, html_content: str, tags: str = "jeces,티스토리") -> dict:
        """
        Playwright를 사용하여 브라우저를 직접 제어해 카카오 계정으로 티스토리에 로그인하고 글을 작성합니다.
        """
        logger.info("Playwright 브라우저 자동화를 시작합니다...")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                # 1. 카카오 티스토리 연동 로그인 페이지 직접 이동
                kakao_login_url = "https://accounts.kakao.com/login?continue=https%3A%2F%2Fwww.tistory.com%2Fauth%2Fext%2Fkakao"
                logger.info(f"카카오 로그인 페이지({kakao_login_url})로 이동합니다...")
                page.goto(kakao_login_url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                # 만약 티스토리 로그인 페이지로 이동된 경우 카카오 로그인 버튼 클릭
                if "tistory.com/auth/login" in page.url:
                    kakao_btn = page.query_selector("a.btn_login.link_kakao") or page.query_selector("a:has-text('카카오계정으로 로그인')")
                    if kakao_btn:
                        kakao_btn.click()
                        page.wait_for_timeout(2000)

                # 2. 아이디 입력 필드 셀렉터 후보군
                id_selectors = [
                    "input[name='loginId']",
                    "#loginId--1",
                    "#input-login_id",
                    "input[type='email']",
                    "input[placeholder*='아이디']",
                    "input[placeholder*='이메일']",
                    "input[type='text']"
                ]

                # 3. 비밀번호 입력 필드 셀렉터 후보군
                pw_selectors = [
                    "input[name='password']",
                    "#password-1",
                    "input[type='password']"
                ]

                # 입력창 대기
                logger.info("로그인 입력 필드를 탐색 중입니다...")
                page.wait_for_selector("input", timeout=10000)

                # 아이디 및 비밀번호 입력
                id_filled = self._fill_first_available(page, id_selectors, self.login_id, "아이디")
                pw_filled = self._fill_first_available(page, pw_selectors, self.login_pw, "비밀번호")

                if not id_filled or not pw_filled:
                    logger.warning("기본 입력 필드를 찾지 못해 전체 input 엘리먼트 순회를 시도합니다.")
                    inputs = page.query_selector_all("input")
                    if len(inputs) >= 2:
                        inputs[0].fill(self.login_id)
                        inputs[1].fill(self.login_pw)
                        logger.info("순서 기반 인풋 입력 성공!")

                # 로그인 버튼 클릭
                logger.info("로그인 버튼을 클릭합니다...")
                submit_btn = (
                    page.query_selector("button.btn_g.highlight.submit") or
                    page.query_selector("button[type='submit']") or
                    page.query_selector("button.btn_confirm") or
                    page.query_selector(".submit")
                )
                if submit_btn:
                    submit_btn.click()
                else:
                    page.keyboard.press("Enter")

                page.wait_for_timeout(4000)

                # 4. 블로그 글쓰기 에디터 페이지로 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"글쓰기 에디터({write_url})로 이동합니다...")
                page.goto(write_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                # 경고 알림(임시저장 확인 등) 팝업 처리
                try:
                    page.on("dialog", lambda dialog: dialog.accept())
                except Exception:
                    pass

                # 5. 에디터 모드를 HTML 모드로 변경
                mode_btn = page.query_selector("#editor-mode-select") or page.query_selector("button:has-text('기본모드')")
                if mode_btn:
                    mode_btn.click()
                    page.wait_for_timeout(500)
                    html_mode_opt = page.query_selector("li:has-text('HTML')") or page.query_selector("button:has-text('HTML')")
                    if html_mode_opt:
                        html_mode_opt.click()
                        page.wait_for_timeout(500)

                # 6. 제목 및 본문 입력
                logger.info("제목과 본문을 입력합니다...")
                title_input = page.query_selector("#post-title-inp") or page.query_selector("textarea.textarea_tit") or page.query_selector("input[placeholder*='제목']")
                if title_input:
                    title_input.fill(title)

                # Playwright JavaScript evaluate를 활용해 에디터에 HTML 주입
                page.evaluate("""
                    (content) => {
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {
                            cm.CodeMirror.setValue(content);
                            return;
                        }
                        if (window.tinymce && window.tinymce.activeEditor) {
                            window.tinymce.activeEditor.setContent(content);
                            return;
                        }
                        const textarea = document.querySelector('textarea.CodeMirror-textarea') || document.querySelector('#editor-contents');
                        if (textarea) {
                            textarea.value = content;
                        }
                    }
                """, html_content)

                # 7. 태그 입력
                if tags:
                    logger.info("태그를 입력합니다...")
                    tag_input = page.query_selector("#tagText") or page.query_selector("input[placeholder*='태그']")
                    if tag_input:
                        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                        for tag in tag_list:
                            tag_input.fill(tag)
                            tag_input.press("Enter")
                            page.wait_for_timeout(300)

                # 8. 발행 버튼 클릭
                logger.info("발행 버튼을 클릭합니다...")
                publish_btn = page.query_selector("#confirm-open-btn") or page.query_selector("button.btn_perform") or page.query_selector("button:has-text('발행')")
                if publish_btn:
                    publish_btn.click()
                    page.wait_for_timeout(1000)

                    final_submit_btn = page.query_selector("#published-btn") or page.query_selector("button.btn_register") or page.query_selector("button:has-text('공개발행')")
                    if final_submit_btn:
                        final_submit_btn.click()
                        page.wait_for_timeout(3000)

                logger.info("🎉 Playwright를 통한 티스토리 포스팅 작성이 완료되었습니다!")
                browser.close()
                return {"success": True, "message": "성공적으로 포스팅이 작성되었습니다."}

            except Exception as e:
                logger.error(f"❌ 브라우저 자동화 실행 중 오류 발생: {e}")
                browser.close()
                return {"success": False, "error": str(e)}
