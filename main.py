import sys
import logging
from config import Config
from content_generator import ContentGenerator
from tistory_browser import TistoryBrowser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def run_auto_blogger():
    logger.info("=== 티스토리 브라우저 원격제어 포스팅 시작 ===")

    missing_env = Config.validate()
    if missing_env:
        logger.error(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_env)}")
        sys.exit(1)

    # 1. 콘텐츠 생성
    logger.info("블로그 포스팅 콘텐츠를 생성 중입니다...")
    generator = ContentGenerator(
        api_key=Config.OPENAI_API_KEY,
        model=Config.OPENAI_MODEL
    )
    title, content, tags = generator.generate_post()
    logger.info(f"생성된 포스팅 제목: {title}")

    # 2. 열려있는 크롬(Port 9222)에 직접 연결하여 포스팅 발행
    logger.info("열려있는 크롬 브라우저 원격제어를 통해 포스팅을 발행합니다...")
    tistory_browser = TistoryBrowser(
        blog_name=Config.TISTORY_BLOG_NAME,
        cdp_url=Config.CDP_URL,
        use_cdp=Config.USE_CDP
    )

    result = tistory_browser.publish_post(
        title=title,
        html_content=content,
        tags=tags
    )

    if result.get("success"):
        logger.info(f"🎉 성공적으로 포스팅 작성이 완료되었습니다!")
    else:
        logger.error(f"❌ 포스팅 실패:\n{result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    run_auto_blogger()
