import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TISTORY_WRITE_URL = "https://www.tistory.com/apis/post/write"

class TistoryAPI:
    def __init__(self, access_token: str, blog_name: str):
        self.access_token = access_token
        self.blog_name = blog_name

    def write_post(self, title: str, content: str, category_id: str = "0", visibility: str = "3", tag: str = "자동작성,AI,블로그"):
        """
        티스토리 오픈 API를 사용하여 포스트를 발행합니다.

        :param title: 포스트 제목
        :param content: 포스트 내용 (HTML 형식)
        :param category_id: 카테고리 ID (기본값 "0")
        :param visibility: 발행 상태 (0: 비공개, 1: 보호, 3: 발행/공개)
        :param tag: 태그 (쉼표로 구분된 문자열)
        :return: API 응답 dict
        """
        data = {
            "access_token": self.access_token,
            "output": "json",
            "blogName": self.blog_name,
            "title": title,
            "content": content,
            "visibility": visibility,
            "category": category_id,
            "tag": tag
        }

        try:
            response = requests.post(TISTORY_WRITE_URL, data=data, timeout=15)
            response.raise_for_status()
            result = response.json()

            tistory_status = result.get("tistory", {}).get("status")
            if tistory_status == "200":
                post_id = result.get("tistory", {}).get("postId")
                url = result.get("tistory", {}).get("url")
                logger.info(f"성공적으로 글이 작성되었습니다. Post ID: {post_id}, URL: {url}")
                return {"success": True, "postId": post_id, "url": url, "data": result}
            else:
                error_reason = result.get("tistory", {}).get("error_reason", "알 수 없는 오류")
                logger.error(f"티스토리 API 오류: {error_reason}")
                return {"success": False, "error": error_reason, "data": result}
        except Exception as e:
            logger.error(f"티스토리 포스트 작성 중 예외 발생: {e}")
            return {"success": False, "error": str(e)}
