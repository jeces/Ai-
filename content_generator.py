import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DAILY_TOPICS = [
    "생산성을 높여주는 AI 활용 꿀팁 5가지",
    "매일매일 실천하는 매일 습관 만들기 가이드",
    "최신 기술 트렌드와 미래 직업 변화",
    "바쁜 현대인을 위한 건강 관리법과 홈 트레이닝",
    "자기계발을 위한 최고의 도서 추천 및 독서 노하우",
    "쉽고 효과적인 블로그 운영 및 수익화 전략",
    "디지털 노마드로 삶을 즐기는 방법과 필수 도구"
]

class ContentGenerator:
    def __init__(self, api_key: str = "", model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def generate_post(self, topic: str = None) -> tuple[str, str, str]:
        """
        블로그 글 (제목, HTML 본문, 태그)을 생성합니다.
        OpenAI API 키가 설정되어 있으면 GPT로 생성하고, 없으면 템플릿 글을 생성합니다.
        """
        if not topic:
            topic = random.choice(DAILY_TOPICS)

        if self.api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.api_key)

                prompt = f"""
다음 주제에 대한 티스토리 블로그 포스팅을 작성해 주세요.
주제: {topic}

요구사항:
1. 독자의 흥미를 끌 수 있는 매력적인 제목을 정해 주세요.
2. HTML 태그(<h2>, <h3>, <p>, <ul>, <li>, <strong> 등)를 사용하여 보기 좋게 스타일링된 본문을 작성하세요.
3. 관련 태그를 3~5개 생성해 주세요 (쉼표로 구분).
4. 결과는 정확히 아래의 JSON 형식으로만 응답해 주세요:
{{
  "title": "제목 내용",
  "content": "HTML 본문 내용",
  "tags": "태그1,태그2,태그3"
}}
"""
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert tech and lifestyle blog writer who writes engaging Korean posts in HTML format."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                import json
                result = json.loads(response.choices[0].message.content)
                title = result.get("title", topic)
                content = result.get("content", f"<p>{topic}</p>")
                tags = result.get("tags", "자동작성,AI,블로그")

                return title, content, tags

            except Exception as e:
                logger.warning(f"OpenAI API 호출 중 오류 발생, 기본 템플릿으로 생성합니다: {e}")

        # OpenAI API가 없거나 오류 발생 시 기본 템플릿으로 포스팅 생성
        today_str = datetime.now().strftime("%Y년 %m월 %d일")
        title = f"[{today_str}] 오늘의 이야기: {topic}"
        content = f"""
<h2>안녕하세요! 오늘 이야기할 주제는 '{topic}' 입니다.</h2>
<p>매일매일 새로운 정보를 공유하고 더 나은 일상을 만들어가는 티스토리 블로그입니다.</p>
<hr/>
<h3>오늘의 주요 내용</h3>
<ul>
  <li><strong>핵심 1:</strong> 지속가능한 목표를 설정하고 작은 것부터 실행하기</li>
  <li><strong>핵심 2:</strong> 효율적인 시간 관리와 도구 활용</li>
  <li><strong>핵심 3:</strong> 매일 꾸준히 기록하며 성장하기</li>
</ul>
<p>여러분도 오늘 하루를 뜻깊게 마무리하시길 바랍니다. 방문해 주셔서 감사합니다!</p>
"""
        tags = "자동작성,일상,정보,블로그"
        return title, content, tags
