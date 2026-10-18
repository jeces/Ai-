import os
from dotenv import load_dotenv

if not os.path.exists(".env") and os.path.exists(".env.txt"):
    try:
        import shutil
        shutil.copy(".env.txt", ".env")
    except Exception:
        pass

load_dotenv(dotenv_path=".env")

class Config:
    TISTORY_LOGIN_ID = os.getenv("TISTORY_LOGIN_ID", "").strip()
    TISTORY_LOGIN_PW = os.getenv("TISTORY_LOGIN_PW", "").strip()
    TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "").strip() or "jeces"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    USE_CDP = os.getenv("USE_CDP", "True").lower() == "true"
    CDP_URL = os.getenv("CDP_URL", "http://localhost:9222").strip()
    USER_DATA_DIR = os.getenv("USER_DATA_DIR", "./user_data").strip()

    @classmethod
    def validate(cls):
        missing = []
        if not os.getenv("TISTORY_BLOG_NAME", "").strip():
            missing.append("TISTORY_BLOG_NAME")

        return missing
