import sys
import logging
from config import Config
from content_generator import ContentGenerator
from tistory_api import TistoryAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def run_auto_blogger():
    logger.info("=== 티스토리 자동 블로그 작성 프로그램 시작 ===")

    missing_env = Config.validate()
    if missing_env:
        logger.error(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_env)}")
        logger.error(".env 파일 또는 환경 변수를 확인해 주세요.")
        sys.exit(1)

    # 1. 콘텐츠 생성
    logger.info("블로그 글 콘텐츠를 생성 중입니다...")
    generator = ContentGenerator(
        api_key=Config.OPENAI_API_KEY,
        model=Config.OPENAI_MODEL
    )
    title, content, tags = generator.generate_post()
    logger.info(f"생성된 글 제목: {title}")

    # 2. 티스토리 업로드
    logger.info("티스토리에 글을 발행 중입니다...")
    tistory = TistoryAPI(
        access_token=Config.TISTORY_ACCESS_TOKEN,
        blog_name=Config.TISTORY_BLOG_NAME
    )

    result = tistory.write_post(
        title=title,
        content=content,
        category_id=Config.TISTORY_CATEGORY_ID,
        visibility=Config.TISTORY_VISIBILITY,
        tag=tags
    )

    if result.get("success"):
        logger.info(f"🎉 성공적으로 포스팅이 완료되었습니다! URL: {result.get('url')}")
    else:
        logger.error(f"❌ 포스팅 실패: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    run_auto_blogger()
