import os
import json
import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ScriptService:

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing in environment variables (.env)")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def load_analysis(self, analysis_file: str) -> dict:
        if not os.path.exists(analysis_file):
            raise FileNotFoundError(f"Analysis file not found: {analysis_file}")
        with open(analysis_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_script(self, analysis: dict, product=None, tone: str = "persuasive") -> str:
        """
        Generate script from analysis dict.
        product: optional SQLAlchemy object or dict. If provided, we include product title and affiliate link in prompt.
        Returns: script text
        """
        summary = analysis.get("summary", "")
        keywords = ", ".join(analysis.get("keywords", []))
        selling_points = "\n".join(f"- {p}" for p in analysis.get("selling_points", []))

        p_title = getattr(product, "title", None) if product else (product or {}).get("title") if isinstance(product, dict) else None
        p_price = getattr(product, "price", None) if product else (product or {}).get("price") if isinstance(product, dict) else None
        p_link = getattr(product, "affiliate_link", None) if product else (product or {}).get("affiliate_link") if isinstance(product, dict) else None

        prompt = f"""
Bạn là một chuyên gia viết kịch bản quảng cáo ngắn cho video (30-60 giây).
Hãy tạo kịch bản dựa trên thông tin dưới đây. Viết ngắn gọn, thu hút, có call-to-action.

Thông tin:
- Tóm tắt: {summary}
- Từ khóa: {keywords}
- Điểm nổi bật:
{selling_points}

{"- Tên sản phẩm: " + str(p_title) if p_title else ""}
{"- Giá: " + str(p_price) + ' USD' if p_price is not None else ""}
{"- Link affiliate: " + str(p_link) if p_link else ""}

Yêu cầu:
- Độ dài phù hợp để đọc trong 30-60 giây (khoảng 80-140 từ).
- Giọng điệu: {tone}
- Kết thúc bằng một CTA rõ ràng: 'Hãy click link trong mô tả để mua ngay!'

Chỉ output kịch bản (không thêm chú thích).
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là chuyên gia viết kịch bản quảng cáo."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=400,
            )
            script = resp.choices[0].message.content.strip()
            return script
        except Exception as e:
            logger.exception("OpenAI error in generate_script")
            fallback = f"{summary}\n\nHãy click link trong mô tả để mua ngay!"
            return fallback

    def generate_script_from_file(self, analysis_file: str, product=None) -> str:
        analysis = self.load_analysis(analysis_file)
        return self.generate_script(analysis, product=product)

    def save_script(self, out_path: str, script_text: str) -> str:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(script_text)
        logger.info("Saved script to %s", out_path)
        return out_path
