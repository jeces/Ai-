import random
import logging
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)

# 인기 블로거들의 인기 주제 카테고리
POPULAR_TOPICS = [
    {"category": "IT/AI", "topic": "2025년 반드시 알아야 할 AI 생산성 앱 TOP 5 (무료 꿀팁)"},
    {"category": "IT/AI", "topic": "ChatGPT로 일하는 시간 절반으로 줄이는 실전 프롬프트 활용법"},
    {"category": "자기계발", "topic": "직장인 퇴근 후 1시간으로 삶을 바꾸는 미라클 루틴 만드는 법"},
    {"category": "자기계발", "topic": "작심삼일 탈출! 습관 형성을 돕는 검증된 뇌과학 원리 3가지"},
    {"category": "트렌드/라이프", "topic": "요즘 트렌디한 사람들의 디지털 노마드 스마트 워크스페이스 구축기"},
    {"category": "재테크/정보", "topic": "사회초년생부터 알고 시작하는 똑똑한 자산 관리 및 절세 꿀팁"},
    {"category": "건강/라이프", "topic": "거북목·굽은 등 안녕! 사무실에서도 할 수 있는 3분 스트레칭"}
]

class ContentGenerator:
    def __init__(self, api_key: str = "", model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def _get_image_url(self, keyword: str) -> str:
        """Unsplash에서 해당 키워드 관련 고화질 대표 이미지 URL을 생성합니다."""
        encoded_kw = urllib.parse.quote(keyword)
        return f"https://source.unsplash.com/1200x630/?{encoded_kw}"

    def generate_post(self, topic: str = None) -> tuple[str, str, str]:
        """
        인기 파워블로거 스타일의 포스팅 (제목, 풍부한 HTML 본문, 태그)을 생성합니다.
        OpenAI API가 있으면 GPT를 사용하고, 없어도 고품질 HTML 템플릿 글을 생성합니다.
        """
        selected_item = random.choice(POPULAR_TOPICS)
        if not topic:
            topic = selected_item["topic"]

        # 고화질 이미지 URL 준비
        main_img = "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80"
        sub_img = "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=1200&q=80"

        if self.api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=self.api_key)

                prompt = f"""
너는 월 방문자수 100만 명을 보유한 대한민국 최고의 인플루언서 IT/라이프스타일 파워블로거야.
블로그 주소는 jeces.tistory.com 스타일이야.

주제: '{topic}'

요구사항:
1. 제목: 클릭을 유도하는 매력적이고 친근한 제목 (예: "🔥 [필독] ...", "💡 ..." 등 포함)
2. 본문 (HTML):
   - 친근하고 친절한 어조 (~했는데요!, ~해보세요😊, ~입니다!)
   - 이모지(✨, 📌, 💡, 🔥, 🚀 등)를 유용하게 배치
   - 시각적 요소:
     - 상단에 메인 이미지 배치: <img src="{main_img}" alt="대표 이미지" style="width:100%; max-width:800px; border-radius:12px; margin:20px 0; display:block;"/>
     - 본문 중간에 보조 이미지 배치: <img src="{sub_img}" alt="상세 이미지" style="width:100%; max-width:800px; border-radius:12px; margin:20px 0; display:block;"/>
     - 이쁜 강조 박스(Callout Box) 활용: <div style="background-color: #f0f7ff; border-left: 5px solid #007bff; padding: 15px; margin: 20px 0; border-radius: 4px;"><strong>💡 한 줄 요약:</strong> ...</div>
     - <h2>, <h3> 소제목으로 깔끔한 단락 구분
     - 핵심 정리 <ul>, <li> 리스트 활용
   - 마무리: 독자에게 댓글과 공감을 유도하는 따뜻한 메시지
3. 태그: 연관 키워드 4~6개 (쉼표 구분)
4. 결과 형식: JSON
{{
  "title": "제목",
  "content": "HTML 본문 전체 내용",
  "tags": "태그1,태그2,태그3"
}}
"""
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a top Korean blog influencer writing highly engaging, aesthetically styled HTML posts."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )

                import json
                result = json.loads(response.choices[0].message.content)
                title = result.get("title", topic)
                content = result.get("content", f"<p>{topic}</p>")
                tags = result.get("tags", "jeces,티스토리,인기블로그,꿀팁")

                return title, content, tags

            except Exception as e:
                logger.warning(f"OpenAI API 호출 중 오류 발생, 고품질 블로거 템플릿으로 생성합니다: {e}")

        # Fallback: 인기 파워블로거 스타일 HTML 템플릿
        today_str = datetime.now().strftime("%Y년 %m월 %d일")
        title = f"🔥 {topic} (실전 꿀팁 총정리)"

        content = f"""
<div style="font-family: 'Noto Sans KR', sans-serif; line-height: 1.8; color: #333;">
  <!-- 메인 헤더 박스 -->
  <div style="background: linear-gradient(135deg, #6e8efb, #a777e3); padding: 25px; border-radius: 12px; color: white; margin-bottom: 25px;">
    <h1 style="margin: 0; font-size: 24px; color: white;">✨ {topic}</h1>
    <p style="margin-top: 10px; font-size: 14px; opacity: 0.9;">작성일: {today_str} | jeces.tistory.com 특별 기획</p>
  </div>

  <p>안녕하세요, 여러분! 👋 매일 알찬 정보와 꿀팁을 전해드리는 <strong>JECES 블로그</strong>에 오신 것을 환영합니다!</p>
  <p>오늘은 많은 분들이 물어보셨던 <strong>'{topic}'</strong>에 대해 알기 쉽게 핵심만 착착 정리해 드리려고 합니다. 끝까지 읽으시면 삶의 질이 200% 올라갈 거예요! 🚀</p>

  <!-- 대표 이미지 -->
  <div style="text-align: center;">
    <img src="{main_img}" alt="대표 이미지" style="width: 100%; max-width: 800px; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />
  </div>

  <!-- 핵심 요약 박스 -->
  <div style="background-color: #f8f9fa; border-left: 5px solid #28a745; padding: 18px; margin: 25px 0; border-radius: 6px;">
    <strong style="color: #28a745; font-size: 16px;">💡 오늘 포스팅의 핵심 Point</strong>
    <ul style="margin-top: 10px; margin-bottom: 0; padding-left: 20px;">
      <li>누구나 따라 할 수 있는 쉬운 단계별 실행 방법</li>
      <li>시간과 비용을 아껴주는 핵심 꿀팁 전격 공개</li>
      <li>실제 적용 시 주의해야 할 체크포인트</li>
    </ul>
  </div>

  <h2 style="border-bottom: 2px solid #6e8efb; padding-bottom: 8px; margin-top: 35px; color: #2c3e50;">1. 왜 지금 이 주제가 주목받을까요? 🤔</h2>
  <p>요즘 트렌드는 빠르게 변화하고 있죠. 바쁜 현대사회에서 효율성을 높이고 삶의 유연성을 확보하는 것이 그 어느 때보다 중요해졌습니다.</p>
  <p>작은 습관과 도구의 차이가 한 달, 1년 뒤에는 엄청난 차이로 다가온다는 사실, 알고 계셨나요? 📌</p>

  <h2 style="border-bottom: 2px solid #6e8efb; padding-bottom: 8px; margin-top: 35px; color: #2c3e50;">2. 실전 적용 가이드 3단계 🛠️</h2>

  <!-- 서브 이미지 -->
  <div style="text-align: center;">
    <img src="{sub_img}" alt="서브 이미지" style="width: 100%; max-width: 800px; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1);" />
  </div>

  <ol style="padding-left: 20px;">
    <li><strong>1단계: 현재 상태 점검하기</strong> - 나에게 가장 필요한 부분이 어디인지 우선순위를 정합니다.</li>
    <li><strong>2단계: 작은 것부터 시도하기</strong> - 처음부터 과도하게 시작하지 않고 하루 10분씩 시작해 보세요.</li>
    <li><strong>3단계: 꾸준한 기록과 피드백</strong> - 매일 기록하며 유의미한 변화를 관찰합니다.</li>
  </ol>

  <!-- 강조 팁 박스 -->
  <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 18px; margin: 25px 0; border-radius: 6px;">
    <strong style="color: #856404; font-size: 16px;">⚠️ 주의할 점!</strong>
    <p style="margin-top: 5px; margin-bottom: 0; color: #856404;">완벽주의보다는 '지속가능함'이 우선입니다. 나만의 페이스를 유지하는 것이 성공의 핵심입니다!</p>
  </div>

  <h2 style="border-bottom: 2px solid #6e8efb; padding-bottom: 8px; margin-top: 35px; color: #2c3e50;">마치며 💬</h2>
  <p>오늘 준비한 내용이 여러분께 작은 도움이 되었기를 바랍니다! 감동받으셨거나 도움이 되셨다면 <strong>공감(❤️)과 댓글</strong> 부탁드려요.</p>
  <p>다음에도 더욱 유익하고 재미있는 콘텐츠로 찾아오겠습니다. 감사합니다! 😊</p>
</div>
"""
        tags = "jeces,티스토리,인기블로그,꿀팁,자기계발,IT트렌드"
        return title, content, tags
