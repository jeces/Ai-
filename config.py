import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TISTORY_LOGIN_ID = os.getenv("TISTORY_LOGIN_ID", "").strip()
    TISTORY_LOGIN_PW = os.getenv("TISTORY_LOGIN_PW", "").strip()
    TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "").strip() or "jeces"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    HEADLESS = os.getenv("HEADLESS", "True").lower() == "true"

    @classmethod
    def validate(cls):
        missing = []
        if not os.getenv("TISTORY_LOGIN_ID", "").strip():
            missing.append("TISTORY_LOGIN_ID")
        if not os.getenv("TISTORY_LOGIN_PW", "").strip():
            missing.append("TISTORY_LOGIN_PW")
        if not os.getenv("TISTORY_BLOG_NAME", "").strip():
            missing.append("TISTORY_BLOG_NAME")

        return missing
