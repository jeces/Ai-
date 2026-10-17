import os
import pytest
from unittest.mock import patch, MagicMock
from config import Config
from tistory_api import TistoryAPI
from content_generator import ContentGenerator

def test_config_validation():
    with patch.dict(os.environ, {"TISTORY_ACCESS_TOKEN": "", "TISTORY_BLOG_NAME": ""}, clear=True):
        missing = Config.validate()
        assert "TISTORY_ACCESS_TOKEN" in missing
        assert "TISTORY_BLOG_NAME" in missing

def test_content_generator_fallback():
    generator = ContentGenerator(api_key="")
    title, content, tags = generator.generate_post(topic="테스트 주제")
    assert "테스트 주제" in title or "테스트 주제" in content
    assert "<img" in content
    assert "jeces" in tags
    assert len(title) > 0
    assert len(content) > 0

def test_tistory_api_write_post_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "tistory": {
            "status": "200",
            "postId": "123",
            "url": "https://jeces.tistory.com/123"
        }
    }

    with patch("requests.post", return_value=mock_response):
        api = TistoryAPI(access_token="test_token", blog_name="jeces")
        result = api.write_post(title="테스트 제목", content="테스트 본문")
        assert result["success"] is True
        assert result["postId"] == "123"
        assert result["url"] == "https://jeces.tistory.com/123"

def test_tistory_api_write_post_failure():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "tistory": {
            "status": "400",
            "error_reason": "접근 권한이 없습니다."
        }
    }

    with patch("requests.post", return_value=mock_response):
        api = TistoryAPI(access_token="invalid_token", blog_name="jeces")
        result = api.write_post(title="테스트 제목", content="테스트 본문")
        assert result["success"] is False
        assert "접근 권한이 없습니다" in result["error"]
