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
    TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "").strip() or "jeces"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    USER_DATA_DIR = os.getenv("USER_DATA_DIR", "./user_data").strip()

    @classmethod
    def validate(cls):
        missing = []
        if not os.getenv("TISTORY_BLOG_NAME", "").strip():
            missing.append("TISTORY_BLOG_NAME")

        return missing
