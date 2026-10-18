import time
import logging
import os
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class TistoryBrowser:
    def __init__(
        self,
        blog_name: str = "jeces",
        cdp_url: str = "http://localhost:9222",
        use_cdp: bool = True
    ):
        self.blog_name = blog_name
        self.cdp_url = cdp_url
        self.use_cdp = use_cdp

    def publish_post(self, title: str, html_content: str, tags: str = "jeces,티스토리") -> dict:
        """
        현재 켜져있는 크롬 브라우저(Port 9222)에 직접 연결하여 로그인되어 있는 상태 그대로 포스팅을 작성합니다.
        새로운 브라우저 창을 띄우지 않고 기존 크롬 창/탭을 활용합니다.
        """
        logger.info(f"열려있는 크롬 브라우저({self.cdp_url})에 원격 연결합니다...")

        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.connect_over_cdp(self.cdp_url)
                logger.info("✅ 현재 열려있는 크롬 브라우저 연결 성공!")
            except Exception as e:
                err_msg = (
                    "열려있는 크롬 브라우저 연결 실패!\n"
                    "크롬이 디버깅 모드(포트 9222)로 켜져 있지 않습니다.\n"
                    "start_chrome_debug.bat 파일이나 아래 명령어로 크롬을 먼저 실행하고 티스토리에 로그인해 주세요:\n"
                    'chrome.exe --remote-debugging-port=9222'
                )
                logger.error(err_msg)
                return {"success": False, "error": err_msg}

            try:
                context = browser.contexts[0] if browser.contexts else browser.new_context()

                # 이미 켜져있는 탭 중 티스토리 관련 탭 찾기, 없으면 활성 탭 사용 또는 새 탭 열기
                page = None
                for p_item in context.pages:
                    if "tistory.com" in p_item.url:
                        page = p_item
                        logger.info(f"기존 열려있는 티스토리 탭({page.url})을 사용합니다.")
                        break

                if not page:
                    page = context.pages[0] if context.pages else context.new_page()

                # 1. 티스토리 글쓰기 에디터 페이지로 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"글쓰기 페이지({write_url})로 이동합니다...")
                page.goto(write_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                # 로그인 확인
                if "auth/login" in page.url or "accounts.kakao.com" in page.url:
                    err_msg = (
                        "현재 열려있는 크롬 창에서 티스토리에 로그인되어 있지 않습니다.\n"
                        "열려있는 크롬 창에서 https://www.tistory.com 에 접속하여 로그인을 완료한 후 다시 실행해 주세요."
                    )
                    logger.error(err_msg)
                    return {"success": False, "error": err_msg}

                # 경고 알림(임시저장 등) 대화상자 수락
                try:
                    page.on("dialog", lambda dialog: dialog.accept())
                except Exception:
                    pass

                # 2. 에디터 모드를 HTML 모드로 변경
                logger.info("HTML 에디터 모드로 전환합니다...")
                mode_btn = page.query_selector("#editor-mode-select") or page.query_selector("button:has-text('기본모드')")
                if mode_btn:
                    mode_btn.click()
                    page.wait_for_timeout(500)
                    html_mode_opt = page.query_selector("li:has-text('HTML')") or page.query_selector("button:has-text('HTML')")
                    if html_mode_opt:
                        html_mode_opt.click()
                        page.wait_for_timeout(500)

                # 3. 제목 및 HTML 본문 작성
                logger.info("제목과 HTML 본문을 입력합니다...")
                title_input = page.query_selector("#post-title-inp") or page.query_selector("textarea.textarea_tit") or page.query_selector("input[placeholder*='제목']")
                if title_input:
                    title_input.fill(title)

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

                # 4. 태그 입력
                if tags:
                    logger.info("태그를 입력합니다...")
                    tag_input = page.query_selector("#tagText") or page.query_selector("input[placeholder*='태그']")
                    if tag_input:
                        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                        for tag in tag_list:
                            tag_input.fill(tag)
                            tag_input.press("Enter")
                            page.wait_for_timeout(300)

                # 5. 발행 버튼 클릭
                logger.info("포스팅 발행 버튼을 클릭합니다...")
                publish_btn = page.query_selector("#confirm-open-btn") or page.query_selector("button.btn_perform") or page.query_selector("button:has-text('발행')")
                if publish_btn:
                    publish_btn.click()
                    page.wait_for_timeout(1500)

                    final_submit_btn = page.query_selector("#published-btn") or page.query_selector("button.btn_register") or page.query_selector("button:has-text('공개발행')")
                    if final_submit_btn:
                        final_submit_btn.click()
                        page.wait_for_timeout(3000)

                logger.info("🎉 현재 열려있는 크롬에서 티스토리 포스팅 작성이 완료되었습니다!")
                return {"success": True, "message": "성공적으로 포스팅이 작성되었습니다."}

            except Exception as e:
                logger.error(f"❌ 포스팅 작성 과정 중 오류 발생: {e}")
                return {"success": False, "error": str(e)}
