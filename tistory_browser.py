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

    def publish_post(self, title: str, html_content: str, tags: str = "jeces,티스토리") -> dict:
        """
        Playwright를 사용하여 브라우저를 직접 제어해 티스토리에 로그인하고 글을 작성합니다.
        """
        logger.info("Playwright 브라우저 자동화를 시작합니다...")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                # 1. 티스토리 로그인 페이지 이동
                logger.info("티스토리 로그인 페이지로 이동합니다...")
                page.goto("https://www.tistory.com/auth/login", wait_until="networkidle")

                # 카카오 계정 로그인 버튼 클릭
                kakao_login_btn = page.query_selector("a.btn_login.link_kakao")
                if kakao_login_btn:
                    kakao_login_btn.click()
                    page.wait_for_load_state("networkidle")

                # 카카오 아이디/비밀번호 입력
                logger.info("카카오 계정 정보를 입력합니다...")
                page.fill("input[name='loginId']", self.login_id)
                page.fill("input[name='password']", self.login_pw)

                # 로그인 버튼 클릭
                page.click("button.btn_g.highlight.submit")
                page.wait_for_timeout(3000)

                # 2. 블로그 글쓰기 에디터 페이지로 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"글쓰기 에디터({write_url})로 이동합니다...")
                page.goto(write_url, wait_until="networkidle")
                page.wait_for_timeout(2000)

                # 경고 알림(임시저장 확인 등) 팝업 처리
                try:
                    page.on("dialog", lambda dialog: dialog.accept())
                except Exception:
                    pass

                # 3. 에디터 모드를 HTML 모드로 변경 (가능한 경우)
                # 에디터 모드 전환 버튼 탐색
                mode_btn = page.query_selector("#editor-mode-select") or page.query_selector("button:has-text('기본모드')")
                if mode_btn:
                    mode_btn.click()
                    page.wait_for_timeout(500)
                    html_mode_opt = page.query_selector("li:has-text('HTML')") or page.query_selector("button:has-text('HTML')")
                    if html_mode_opt:
                        html_mode_opt.click()
                        page.wait_for_timeout(500)

                # 4. 제목 및 본문 입력
                logger.info("제목과 본문을 입력합니다...")

                # 제목 입력
                title_input = page.query_selector("#post-title-inp") or page.query_selector("textarea.textarea_tit") or page.query_selector("input[placeholder*='제목']")
                if title_input:
                    title_input.fill(title)
                else:
                    logger.warning("제목 입력 필드를 찾는 데 실패했습니다.")

                # HTML 본문 입력 (에디터 iframe 또는 CodeMirror / textarea)
                content_editor = page.query_selector("textarea.CodeMirror-textarea") or page.query_selector("#mce_0_ifr") or page.query_selector("#editor-mode-select")

                # Playwright JavaScript evaluate를 활용해 에디터에 HTML 주입
                page.evaluate("""
                    (content) => {
                        // CodeMirror 에디터 지원
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {
                            cm.CodeMirror.setValue(content);
                            return;
                        }
                        // TinyMCE 에디터 지원
                        if (window.tinymce && window.tinymce.activeEditor) {
                            window.tinymce.activeEditor.setContent(content);
                            return;
                        }
                        // 일반 textarea 지원
                        const textarea = document.querySelector('textarea.CodeMirror-textarea') || document.querySelector('#editor-contents');
                        if (textarea) {
                            textarea.value = content;
                        }
                    }
                """, html_content)

                # 5. 태그 입력
                if tags:
                    logger.info("태그를 입력합니다...")
                    tag_input = page.query_selector("#tagText") or page.query_selector("input[placeholder*='태그']")
                    if tag_input:
                        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                        for tag in tag_list:
                            tag_input.fill(tag)
                            tag_input.press("Enter")
                            page.wait_for_timeout(300)

                # 6. 발행 버튼 클릭
                logger.info("발행 버튼을 클릭합니다...")
                publish_btn = page.query_selector("#confirm-open-btn") or page.query_selector("button.btn_perform") or page.query_selector("button:has-text('발행')")
                if publish_btn:
                    publish_btn.click()
                    page.wait_for_timeout(1000)

                    # 공개 설정 및 최종 발행 확인 버튼 클릭
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
