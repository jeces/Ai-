import time
import logging
import os
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class TistoryBrowser:
    def __init__(
        self,
        login_id: str = "",
        login_pw: str = "",
        blog_name: str = "jeces",
        headless: bool = False,
        use_cdp: bool = True,
        cdp_url: str = "http://localhost:9222",
        user_data_dir: str = "./user_data"
    ):
        self.login_id = login_id
        self.login_pw = login_pw
        self.blog_name = blog_name
        self.headless = headless
        self.use_cdp = use_cdp
        self.cdp_url = cdp_url
        self.user_data_dir = os.path.abspath(user_data_dir)

    def publish_post(self, title: str, html_content: str, tags: str = "jeces,티스토리") -> dict:
        """
        Playwright를 사용해 이미 로그인된 브라우저(CDP 연결 또는 Persistent Profile)를 제어하여 포스팅을 올립니다.
        """
        logger.info("Playwright 브라우저 자동화를 시작합니다...")

        with sync_playwright() as p:
            browser = None
            context = None
            page = None
            is_cdp = False

            try:
                # 방법 1: 열려있는 크롬(CDP 9222 포트)에 원격 연결
                if self.use_cdp:
                    try:
                        logger.info(f"이미 열려있는 크롬 브라우저({self.cdp_url})에 원격 연결을 시도합니다...")
                        browser = p.chromium.connect_over_cdp(self.cdp_url)
                        context = browser.contexts[0] if browser.contexts else browser.new_context()
                        page = context.new_page() if not context.pages else context.pages[0]
                        is_cdp = True
                        logger.info("✅ 열려있는 크롬 브라우저 연결 성공!")
                    except Exception as cdp_err:
                        logger.warning(f"CDP 원격 크롬 연결 실패: {cdp_err}. 저장된 사용자 데이터 프로필로 브라우저를 실행합니다.")

                # 방법 2: 저장된 쿠키/프로필 세션으로 브라우저 실행 (Persistent Context)
                if not page:
                    logger.info(f"사용자 세션 데이터 경로({self.user_data_dir})로 크롬 브라우저를 엽니다...")
                    context = p.chromium.launch_persistent_context(
                        self.user_data_dir,
                        headless=self.headless,
                        channel="chrome",
                        args=["--no-sandbox", "--disable-setuid-sandbox"]
                    )
                    page = context.new_page() if not context.pages else context.pages[0]

                # 1. 티스토리 글쓰기 에디터 페이지로 직접 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"티스토리 글쓰기 에디터({write_url})로 이동합니다...")
                page.goto(write_url, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)

                # 로그인 안 되어있어서 로그인 페이지로 튕긴 경우 자동 로그인 시도
                if "auth/login" in page.url or "accounts.kakao.com" in page.url:
                    logger.info("현재 로그인되어 있지 않아 로그인 절차를 시도합니다...")
                    if "tistory.com/auth/login" in page.url:
                        kakao_btn = page.query_selector("a.btn_login.link_kakao") or page.query_selector("a:has-text('카카오계정으로 로그인')")
                        if kakao_btn:
                            kakao_btn.click()
                            page.wait_for_timeout(2000)

                    if self.login_id and self.login_pw:
                        id_selectors = ["input[name='loginId']", "#loginId--1", "input[type='email']", "input[type='text']"]
                        pw_selectors = ["input[name='password']", "#password-1", "input[type='password']"]

                        for s in id_selectors:
                            el = page.query_selector(s)
                            if el and el.is_visible():
                                el.fill(self.login_id)
                                break
                        for s in pw_selectors:
                            el = page.query_selector(s)
                            if el and el.is_visible():
                                el.fill(self.login_pw)
                                break

                        submit_btn = page.query_selector("button.btn_g.highlight.submit") or page.query_selector("button[type='submit']")
                        if submit_btn:
                            submit_btn.click()
                            page.wait_for_timeout(4000)

                    # 로그인 후 다시 글쓰기 페이지로 이동
                    page.goto(write_url, wait_until="domcontentloaded")
                    page.wait_for_timeout(3000)

                # 경고 알림(임시저장 확인 등) 팝업 자동 수락
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
                logger.info("제목과 HTML 본문을 입력 중입니다...")
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

                logger.info("🎉 포스팅 작성이 성공적으로 완료되었습니다!")

                # CDP로 직접 연 크롬인 경우 탭만 닫고 닫지 않음
                if not is_cdp and context:
                    context.close()

                return {"success": True, "message": "성공적으로 포스팅이 작성되었습니다."}

            except Exception as e:
                logger.error(f"❌ 포스팅 진행 중 오류 발생: {e}")
                if not is_cdp and context:
                    try:
                        context.close()
                    except Exception:
                        pass
                return {"success": False, "error": str(e)}
