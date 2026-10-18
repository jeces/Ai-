import time
import logging
import os
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class TistoryBrowser:
    def __init__(
        self,
        blog_name: str = "jeces",
        headless: bool = False,
        user_data_dir: str = "./user_data"
    ):
        self.blog_name = blog_name
        self.headless = headless
        self.user_data_dir = os.path.abspath(user_data_dir)

    def publish_post(self, title: str, html_content: str, tags: str = "jeces,티스토리") -> dict:
        """
        1. 크롬 브라우저 창을 엽니다.
        2. 티스토리/카카오 로그인 페이지로 이동하여 사용자가 직접 로그인할 수 있게 기다립니다.
        3. 로그인 완료가 감지되면 자동으로 글쓰기 페이지로 이동하여 제목, 이미지/HTML 본문, 태그를 입력하고 발행합니다.
        """
        logger.info("Playwright 크롬 브라우저를 오픈합니다...")

        with sync_playwright() as p:
            try:
                # 사용자 세션 쿠키가 저장되는 크롬 브라우저 실행
                context = p.chromium.launch_persistent_context(
                    self.user_data_dir,
                    headless=False,  # 사용자가 눈으로 보고 로그인해야 하므로 항상 창을 띄움
                    channel="chrome",
                    viewport={"width": 1280, "height": 850},
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
            except Exception as e:
                logger.warning(f"시스템 설치 크롬 실행 실패: {e}. 기본 Chromium으로 실행합니다.")
                context = p.chromium.launch_persistent_context(
                    self.user_data_dir,
                    headless=False,
                    viewport={"width": 1280, "height": 850},
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )

            page = context.pages[0] if context.pages else context.new_page()

            try:
                # 1. 로그인 여부 확인 및 수동 로그인 유도
                check_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"블로그 접근 확인 중... ({check_url})")
                page.goto(check_url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                if "auth/login" in page.url or "accounts.kakao.com" in page.url or "tistory.com/auth" in page.url:
                    login_url = "https://www.tistory.com/auth/login"
                    logger.info("===================================================")
                    logger.info("🔑 [로그인 필요] 화면에 열린 크롬 브라우저 창에서 카카오/티스토리 로그인을 직접 완료해 주세요.")
                    logger.info("===================================================")

                    page.goto(login_url, wait_until="domcontentloaded")

                    # 사용자가 로그인을 완료할 때까지 대기 (최대 180초)
                    logged_in = False
                    start_time = time.time()
                    while time.time() - start_time < 180:
                        try:
                            current_url = page.url
                            if "tistory.com" in current_url and "auth/login" not in current_url and "accounts.kakao" not in current_url:
                                logged_in = True
                                logger.info("✅ 로그인 완료가 감지되었습니다! 자동 포스팅을 시작합니다.")
                                break
                        except Exception:
                            pass
                        time.sleep(2)

                    if not logged_in:
                        logger.error("❌ 로그인 시간이 초과되었습니다 (3분 제한).")
                        context.close()
                        return {"success": False, "error": "로그인 시간 초과 (3분 내에 로그인을 완료해 주세요)"}

                # 2. 로그인 완료 후 글쓰기 에디터 페이지로 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"글쓰기 에디터 페이지({write_url})로 이동 중...")
                page.goto(write_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                # 경고 알림(임시저장 알림 등) 팝업 수락
                try:
                    page.on("dialog", lambda dialog: dialog.accept())
                except Exception:
                    pass

                # 3. 에디터 모드를 HTML 모드로 전환
                logger.info("에디터 모드를 HTML 모드로 변경합니다...")
                mode_btn = page.query_selector("#editor-mode-select") or page.query_selector("button:has-text('기본모드')")
                if mode_btn:
                    mode_btn.click()
                    page.wait_for_timeout(500)
                    html_mode_opt = page.query_selector("li:has-text('HTML')") or page.query_selector("button:has-text('HTML')")
                    if html_mode_opt:
                        html_mode_opt.click()
                        page.wait_for_timeout(500)

                # 4. 제목 및 HTML 본문 자동 작성
                logger.info("제목과 본문을 입력하는 중입니다...")
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

                # 6. 발행 버튼 자동 클릭
                logger.info("발행 버튼을 클릭합니다...")
                publish_btn = page.query_selector("#confirm-open-btn") or page.query_selector("button.btn_perform") or page.query_selector("button:has-text('발행')")
                if publish_btn:
                    publish_btn.click()
                    page.wait_for_timeout(1500)

                    final_submit_btn = page.query_selector("#published-btn") or page.query_selector("button.btn_register") or page.query_selector("button:has-text('공개발행')")
                    if final_submit_btn:
                        final_submit_btn.click()
                        page.wait_for_timeout(4000)

                logger.info("🎉 포스팅 발행이 완료되었습니다! 다음 실행 시에는 세션이 유지되어 자동으로 작성됩니다.")
                context.close()
                return {"success": True, "message": "성공적으로 포스팅이 작성되었습니다."}

            except Exception as e:
                logger.error(f"❌ 포스팅 작성 도중 오류가 발생했습니다: {e}")
                try:
                    context.close()
                except Exception:
                    pass
                return {"success": False, "error": str(e)}
