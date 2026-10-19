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
                check_url = f"https://{self.blog_name}.tistory.com/manage/newpost"
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
                            # 브라우저 페이지 탐색 중 간섭(goto) 없이 URL 리다이렉션 결과만 능동 모니터링
                            for p in context.pages:
                                u = p.url
                                # 로그인/인증 리다이렉트가 끝나고 티스토리 본체 페이지로 돌아왔는지 확인
                                if "tistory.com" in u and all(x not in u for x in ["auth", "accounts.kakao", "redirect", "login"]):
                                    logged_in = True
                                    page = p
                                    logger.info(f"🎉 로그인 성공 감지! (도착 URL: {u})")
                                    break

                            if logged_in:
                                break

                        except Exception as e:
                            logger.debug(f"로그인 감지 중 예외: {e}")

                        time.sleep(1.5)
                    page.wait_for_timeout(2000)

                    if not logged_in:
                        error_msg = "로그인 대기 시간이 초과되었습니다 (3분 내 로그인 필요)."
                        logger.error(f"❌ {error_msg}")
                        if not is_cdp:
                            context.close()
                        return {"success": False, "error": error_msg}

                # 2. 글쓰기 에디터 페이지로 이동
                write_url = f"https://{self.blog_name}.tistory.com/manage/newpost"
                logger.info(f"글쓰기 에디터({write_url})로 이동 중...")

                # 브라우저 다이얼로그(임시저장 복구 확인 등) 거절 처리로 기존 저장글 이어쓰기 방지
                def handle_dialog(dialog):
                    msg = dialog.message
                    if any(x in msg for x in ["임시", "복구", "불러"]):
                        logger.info(f"임시저장 복구 확인 창 감지 -> 거절(dismiss) 처리: {msg}")
                        dialog.dismiss()
                    else:
                        dialog.accept()

                try:
                    page.on("dialog", handle_dialog)
                except Exception:
                    pass

                page.goto(write_url, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)

                # DOM 팝업(임시저장 복구 등) 취소/새로작성 클릭
                try:
                    cancel_btn = page.query_selector("button:has-text('취소'), .btn_cancel, button:has-text('아니오'), button:has-text('새로 작성')")
                    if cancel_btn and cancel_btn.is_visible():
                        cancel_btn.click()
                        logger.info("기존 임시 저장 복구 팝업(취소/새로 작성)을 클릭했습니다.")
                        page.wait_for_timeout(1000)
                except Exception:
                    pass

                # 3. 에디터 모드를 HTML 모드로 변경
                logger.info("에디터 모드를 HTML 모드로 전환합니다...")
                try:
                    mode_btn = page.wait_for_selector("#editor-mode-select, button:has-text('기본모드'), #mceu_18-open, .btn_mode", timeout=12000)
                    if mode_btn:
                        mode_btn.click()
                        page.wait_for_timeout(600)
                        html_mode_opt = page.wait_for_selector("li:has-text('HTML'), button:has-text('HTML'), span:has-text('HTML'), #editor-mode-select-html", timeout=5000)
                        if html_mode_opt:
                            html_mode_opt.click()
                            page.wait_for_timeout(1000)
                            try:
                                alert_ok = page.query_selector("button:has-text('확인'), .btn_confirm, .confirm")
                                if alert_ok and alert_ok.is_visible():
                                    alert_ok.click()
                                    page.wait_for_timeout(500)
                            except Exception:
                                pass
                except Exception as e:
                    logger.warning(f"에디터 모드 전환 탐색 경고: {e}")

                # 4. 제목 입력 (기존 내용 완전 삭제 후 새 제목 작성)
                logger.info("제목을 입력합니다...")
                title_selector = "#post-title-inp, textarea.textarea_tit, input[placeholder*='제목'], textarea[placeholder*='제목']"
                try:
                    title_input = page.wait_for_selector(title_selector, timeout=10000)
                    if title_input:
                        title_input.click()
                        title_input.focus()
                        title_input.fill("")
                        page.wait_for_timeout(200)
                        title_input.fill(title)
                        title_input.dispatch_event("input")
                        title_input.dispatch_event("change")
                        logger.info("✅ 제목 입력 성공!")
                except Exception as e:
                    err_msg = f"제목 입력란을 찾을 수 없습니다: {e}"
                    logger.error(f"❌ {err_msg}")
                    if not is_cdp:
                        context.close()
                    return {"success": False, "error": err_msg}

                # 5. 기존 본문 초기화 후 새 HTML 본문 작성
                logger.info("HTML 본문을 작성합니다 (기존 내용 초기화 후 주입)...")
                inserted = page.evaluate("""
                    (content) => {
                        let success = false;

                        // 1. CodeMirror 에디터 (HTML 모드)
                        const cm = document.querySelector('.CodeMirror');
                        if (cm && cm.CodeMirror) {
                            cm.CodeMirror.setValue('');
                            cm.CodeMirror.setValue(content);
                            if (typeof cm.CodeMirror.save === 'function') cm.CodeMirror.save();
                            if (typeof cm.CodeMirror.refresh === 'function') cm.CodeMirror.refresh();
                            success = true;
                        }

                        // 2. ProseMirror / Contenteditable 에디터 (기본 모드 또는 블록 에디터)
                        const ce = document.querySelector('.ProseMirror, [contenteditable="true"], .tt-content');
                        if (ce) {
                            ce.focus();
                            ce.innerHTML = content;
                            ce.dispatchEvent(new Event('input', { bubbles: true }));
                            ce.dispatchEvent(new Event('change', { bubbles: true }));
                            ce.dispatchEvent(new Event('keyup', { bubbles: true }));
                            success = true;
                        }

                        // 3. TinyMCE activeEditor
                        if (window.tinymce && window.tinymce.activeEditor) {
                            window.tinymce.activeEditor.setContent('');
                            window.tinymce.activeEditor.setContent(content);
                            if (typeof window.tinymce.activeEditor.save === 'function') window.tinymce.activeEditor.save();
                            success = true;
                        }

                        // 4. TinyMCE iframe
                        const iframe = document.querySelector('iframe#tinymce_ifr, iframe[title*="Rich Text Area"], iframe.mce-edit-area');
                        if (iframe && iframe.contentDocument) {
                            const body = iframe.contentDocument.querySelector('body');
                            if (body) {
                                body.innerHTML = content;
                                success = true;
                            }
                        }

                        // 5. Fallback textarea
                        const textarea = document.querySelector('textarea.CodeMirror-textarea') || document.querySelector('#editor-contents');
                        if (textarea) {
                            textarea.value = content;
                            textarea.dispatchEvent(new Event('input', { bubbles: true }));
                            textarea.dispatchEvent(new Event('change', { bubbles: true }));
                            success = true;
                        }

                        return success;
                    }
                """, html_content)

                # 클립보드 붙여넣기 보조 방식
                if not inserted:
                    try:
                        logger.info("자바스크립트 직접 주입 실패 -> 클립보드 붙여넣기 및 키보드 입력 시도...")
                        editor_area = page.query_selector(".CodeMirror, .ProseMirror, [contenteditable='true'], #editor-contents")
                        if editor_area:
                            editor_area.click()
                            page.evaluate("content => navigator.clipboard.writeText(content)", html_content)
                            page.keyboard.press("Control+A")
                            page.keyboard.press("Control+V")
                            inserted = True
                    except Exception as paste_err:
                        logger.warning(f"클립보드 붙여넣기 시도 오류: {paste_err}")

                logger.info(f"✅ 본문 내용 작성 시도 완료 (결과: {inserted})")

                # 6. 태그 입력
                if tags:
                    logger.info("태그를 입력합니다...")
                    try:
                        tag_input = page.query_selector("#inp_tag, #tagText, input[placeholder*='태그']")
                        if tag_input:
                            tag_input.click()
                            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
                            for tag in tag_list:
                                tag_input.fill(tag)
                                page.keyboard.press("Enter")
                                page.wait_for_timeout(300)
                            logger.info("✅ 태그 입력 성공!")
                    except Exception as e:
                        logger.warning(f"태그 입력 중 경고: {e}")

                # 7. 발행 버튼 클릭
                logger.info("발행 버튼을 클릭합니다...")
                try:
                    # 1단계: 에디터 하단 '완료' 또는 '발행' 버튼 클릭
                    publish_btn_selector = "#confirm-open-btn, button:has-text('완료'), button:has-text('발행'), button.btn_perform, button.btn_submit, #open-btn"
                    publish_btn = page.wait_for_selector(publish_btn_selector, timeout=10000)
                    if publish_btn:
                        publish_btn.click()
                        logger.info("1단계 완료/발행 버튼을 클릭했습니다.")
                        page.wait_for_timeout(2000)

                        # 2단계: 공개발행 레이어/패널 내의 최종 '공개발행' 버튼 클릭
                        final_submit_selector = "#published-btn, button:has-text('공개발행'), button.btn_register, button.btn_post, button:has-text('발행하기')"
                        try:
                            final_submit_btn = page.wait_for_selector(final_submit_selector, timeout=8000)
                            if final_submit_btn:
                                final_submit_btn.click()
                                page.wait_for_timeout(4000)
                                logger.info("✅ 최종 공개발행 완료 버튼 클릭 성공!")
                        except Exception:
                            logger.info("추가 발행 레이어가 없거나 이미 발행이 진행 중입니다.")

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
