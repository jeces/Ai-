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
        use_cdp: bool = False,
        cdp_url: str = "http://localhost:9222",
        user_data_dir: str = "./user_data"
    ):
        self.blog_name = blog_name
        self.headless = headless
        self.use_cdp = use_cdp
        self.cdp_url = cdp_url
        self.user_data_dir = os.path.abspath(user_data_dir)

    def publish_post(self, title: str, html_content: str, tags: str = "jeces,티스토리") -> dict:
        """
        1. 열려있는 크롬 브라우저(CDP)에 연결하거나, Persistent Context로 크롬 브라우저를 오픈합니다.
        2. 티스토리 로그인 여부를 자동으로 확인하며, 미로그인 시 로그인 완료를 자동 감지합니다.
        3. 명시적 가시성 대기(wait_for_selector)를 사용하여 에디터 조작, 제목/본문/태그 작성 및 발행을 확실하게 수행합니다.
        """
        logger.info("Playwright 크롬 브라우저 자동화를 준비합니다...")

        with sync_playwright() as p:
            context = None
            browser = None
            is_cdp = False

            # 방법 1: 열려있는 디버깅 크롬에 CDP 연결 시도
            if self.use_cdp:
                try:
                    logger.info(f"열려있는 디버깅 크롬({self.cdp_url})에 원격 연결을 시도합니다...")
                    browser = p.chromium.connect_over_cdp(self.cdp_url)
                    context = browser.contexts[0] if browser.contexts else browser.new_context()
                    is_cdp = True
                    logger.info("✅ 열려있는 크롬 브라우저 연결 성공!")
                except Exception as cdp_err:
                    logger.info(f"CDP 연결 없음 ({cdp_err}). 독립 브라우저로 실행합니다.")

            # 방법 2: 세션 유지를 위한 Persistent Context 실행
            if not context:
                try:
                    context = p.chromium.launch_persistent_context(
                        self.user_data_dir,
                        headless=self.headless,
                        channel="chrome",
                        viewport={"width": 1280, "height": 850},
                        args=["--no-sandbox", "--disable-setuid-sandbox"]
                    )
                except Exception as e:
                    logger.warning(f"시스템 설치 크롬 실행 실패: {e}. 기본 Chromium으로 실행합니다.")
                    context = p.chromium.launch_persistent_context(
                        self.user_data_dir,
                        headless=self.headless,
                        viewport={"width": 1280, "height": 850},
                        args=["--no-sandbox", "--disable-setuid-sandbox"]
                    )

            page = context.pages[0] if context.pages else context.new_page()

            try:
                # 1. 로그인 여부 확인 및 자동 감지
                check_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"티스토리 글쓰기 페이지 접근 확인 중... ({check_url})")
                page.goto(check_url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                # 로그인 페이지로 리다이렉트된 경우
                if "auth/login" in page.url or "accounts.kakao.com" in page.url or "tistory.com/auth" in page.url:
                    login_url = "https://www.tistory.com/auth/login"
                    logger.info("===================================================")
                    logger.info("🔑 [로그인 필요] 화면에 열린 브라우저에서 카카오/티스토리 로그인을 완료해 주세요!")
                    logger.info("로그인이 완료되면 자동으로 감지하여 포스팅 작성을 진행합니다.")
                    logger.info("===================================================")

                    page.goto(login_url, wait_until="domcontentloaded")

                    # 로그인 완료 자동 감지 (최대 180초 대기)
                    logged_in = False
                    start_time = time.time()
                    last_log_time = 0

                    while time.time() - start_time < 180:
                        now = time.time()
                        if now - last_log_time >= 5:
                            logger.info("⏳ 로그인 완료 감지 대기 중... (브라우저에서 로그인을 진행해 주세요)")
                            last_log_time = now

                        try:
                            # 1. context 내의 모든 페이지 URL 점검
                            for p in context.pages:
                                u = p.url
                                if "tistory.com" in u and "auth/login" not in u and "accounts.kakao" not in u:
                                    logged_in = True
                                    logger.info(f"🎉 로그인 성공 감지! (감지 URL: {u})")
                                    page = p
                                    break

                            if logged_in:
                                break

                            # 2. 쿠키 기반 로그인 확인
                            cookies = context.cookies()
                            cookie_names = [c.get("name", "") for c in cookies]
                            if "TSSESSION" in cookie_names or "_T_AUTH" in cookie_names or "TSID" in cookie_names:
                                logged_in = True
                                logger.info("🎉 로그인 쿠키(TSSESSION/_T_AUTH)가 확인되었습니다!")
                                break

                        except Exception as e:
                            logger.debug(f"로그인 감지 중 예외: {e}")

                        time.sleep(1.5)

                    if not logged_in:
                        error_msg = "로그인 대기 시간이 초과되었습니다 (3분 내 로그인 필요)."
                        logger.error(f"❌ {error_msg}")
                        if not is_cdp:
                            context.close()
                        return {"success": False, "error": error_msg}

                # 2. 글쓰기 에디터 페이지로 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/post"
                logger.info(f"글쓰기 에디터({write_url})로 이동 중...")

                # 브라우저 다이얼로그(alert/confirm) 자동 승인 설정
                try:
                    page.on("dialog", lambda dialog: dialog.accept())
                except Exception:
                    pass

                page.goto(write_url, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                # 모달 팝업(임시저장 복구 등) 처리
                try:
                    cancel_btn = page.query_selector("button:has-text('취소'), .btn_cancel, button:has-text('아니오')")
                    if cancel_btn and cancel_btn.is_visible():
                        cancel_btn.click()
                        logger.info("임시 저장 복구 팝업(취소)을 클릭했습니다.")
                        page.wait_for_timeout(500)
                except Exception:
                    pass

                # 3. 에디터 모드를 HTML 모드로 변경 (명시적 요소 대기)
                logger.info("에디터 모드를 HTML 모드로 전환합니다...")
                try:
                    mode_btn = page.wait_for_selector("#editor-mode-select, button:has-text('기본모드')", timeout=8000)
                    if mode_btn:
                        mode_btn.click()
                        page.wait_for_timeout(500)
                        html_mode_opt = page.wait_for_selector("li:has-text('HTML'), button:has-text('HTML')", timeout=5000)
                        if html_mode_opt:
                            html_mode_opt.click()
                            page.wait_for_timeout(500)
                            # 모드 변경 확인 팝업 시
                            try:
                                alert_ok = page.query_selector("button:has-text('확인')")
                                if alert_ok and alert_ok.is_visible():
                                    alert_ok.click()
                                    page.wait_for_timeout(500)
                            except Exception:
                                pass
                except Exception as e:
                    logger.warning(f"에디터 모드 전환 버튼 탐색 경고 (기본 모드로 계속 진행): {e}")

                # 4. 제목 입력 (명시적 대기 및 에러 검증)
                logger.info("제목을 입력합니다...")
                title_selector = "#post-title-inp, textarea.textarea_tit, input[placeholder*='제목']"
                try:
                    title_input = page.wait_for_selector(title_selector, timeout=10000)
                    if title_input:
                        title_input.fill(title)
                        logger.info("✅ 제목 입력 성공!")
                except Exception as e:
                    err_msg = f"제목 입력란을 찾을 수 없습니다: {e}"
                    logger.error(f"❌ {err_msg}")
                    if not is_cdp:
                        context.close()
                    return {"success": False, "error": err_msg}

                # 5. HTML 본문 작성
                logger.info("HTML 본문을 입력합니다...")
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
                logger.info("✅ 본문 내용 작성 성공!")

                # 6. 태그 입력
                if tags:
                    logger.info("태그를 입력합니다...")
                    try:
                        tag_input = page.query_selector("#tagText, input[placeholder*='태그']")
                        if tag_input:
                            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                            for tag in tag_list:
                                tag_input.fill(tag)
                                tag_input.press("Enter")
                                page.wait_for_timeout(300)
                            logger.info("✅ 태그 입력 성공!")
                    except Exception as e:
                        logger.warning(f"태그 입력 중 경고: {e}")

                # 7. 발행 버튼 클릭
                logger.info("발행 버튼을 클릭합니다...")
                try:
                    publish_btn = page.wait_for_selector("#confirm-open-btn, button.btn_perform, button:has-text('발행')", timeout=10000)
                    if publish_btn:
                        publish_btn.click()
                        page.wait_for_timeout(1500)

                        final_submit_btn = page.wait_for_selector("#published-btn, button.btn_register, button:has-text('공개발행')", timeout=10000)
                        if final_submit_btn:
                            final_submit_btn.click()
                            page.wait_for_timeout(4000)
                            logger.info("✅ 공개발행 완료 버튼 클릭 성공!")
                except Exception as e:
                    err_msg = f"발행 버튼 클릭 중 오류가 발생했습니다: {e}"
                    logger.error(f"❌ {err_msg}")
                    if not is_cdp:
                        context.close()
                    return {"success": False, "error": err_msg}

                logger.info("🎉 티스토리 블로그 포스팅 작성이 정상 완료되었습니다!")
                if not is_cdp:
                    context.close()

                return {"success": True, "message": "성공적으로 포스팅이 작성되었습니다."}

            except Exception as e:
                logger.error(f"❌ 포스팅 작성 과정 중 예외가 발생했습니다: {e}")
                if not is_cdp and context:
                    try:
                        context.close()
                    except Exception:
                        pass
                return {"success": False, "error": str(e)}
