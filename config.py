import os
from dotenv import load_dotenv

# .env 파일이 존재하면 로드
load_dotenv()

class Config:
    TISTORY_ACCESS_TOKEN = os.getenv("TISTORY_ACCESS_TOKEN", "").strip()
    TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "").strip()
    TISTORY_CATEGORY_ID = os.getenv("TISTORY_CATEGORY_ID", "0").strip()
    TISTORY_VISIBILITY = os.getenv("TISTORY_VISIBILITY", "3").strip() # 3: 공개, 0: 비공개

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    @classmethod
    def validate(cls):
        missing = []
        if not cls.TISTORY_ACCESS_TOKEN:
            missing.append("TISTORY_ACCESS_TOKEN")
        if not cls.TISTORY_BLOG_NAME:
            missing.append("TISTORY_BLOG_NAME")

        return missing
