import os
import pytest
from unittest.mock import patch, MagicMock
from config import Config
from tistory_browser import TistoryBrowser
from content_generator import ContentGenerator

def test_config_validation():
    with patch.dict(os.environ, {"TISTORY_LOGIN_ID": "", "TISTORY_LOGIN_PW": "", "TISTORY_BLOG_NAME": ""}, clear=True):
        missing = Config.validate()
        assert "TISTORY_LOGIN_ID" in missing
        assert "TISTORY_LOGIN_PW" in missing
        assert "TISTORY_BLOG_NAME" in missing

def test_content_generator_fallback():
    generator = ContentGenerator(api_key="")
    title, content, tags = generator.generate_post(topic="테스트 주제")
    assert "테스트 주제" in title or "테스트 주제" in content
    assert "<img" in content
    assert "jeces" in tags
    assert len(title) > 0
    assert len(content) > 0

@patch("tistory_browser.sync_playwright")
def test_tistory_browser_publish_post_success(mock_playwright):
    mock_p = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()

    mock_playwright.return_value.__enter__.return_value = mock_p
    mock_p.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_element = MagicMock()
    mock_element.is_visible.return_value = True
    mock_page.query_selector.return_value = mock_element

    tb = TistoryBrowser(login_id="test_id", login_pw="test_pw", blog_name="jeces", headless=True)
    result = tb.publish_post(title="테스트 제목", html_content="<p>테스트 본문</p>", tags="테스트,태그")

    assert result["success"] is True
    assert "성공적으로" in result["message"]
