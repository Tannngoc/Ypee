import os
import json
import re
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AnalyzerService:
    """
    Phân tích product (dùng OpenAI) -> trả về dict:
    { "summary": str, "keywords": [..], "selling_points": [..] }
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing in environment variables (.env)")
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def analyze_product(self, product) -> dict:
        """
        product: SQLAlchemy object or any object with .title, .description, .price attributes
        returns: analysis dict
        """
        title = getattr(product, "title", "")
        desc = getattr(product, "description", "") or "Không có mô tả"
        price = getattr(product, "price", None)

        prompt = f"""
Bạn là một chuyên gia marketing. Hãy phân tích sản phẩm sau và trả về kết quả đúng định dạng JSON.

Tên sản phẩm: {title}
Mô tả: {desc}
Giá: {price}

Yêu cầu:
- Trả về JSON duy nhất với cấu trúc:
{{
  "summary": "Tóm tắt ngắn gọn sản phẩm (1-2 câu)",
  "keywords": ["từ khóa 1", "từ khóa 2"],
  "selling_points": ["Điểm mạnh 1", "Điểm mạnh 2"]
}}
KHÔNG THÊM BẤT KỲ LỜI GIẢI THÍCH NÀO KHÁC.
"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=300,
            )
            content = resp.choices[0].message.content.strip()
        except Exception as e:
            logger.exception("OpenAI request failed in analyze_product")
            return {"summary": "", "keywords": [], "selling_points": []}

        parsed = self._extract_json(content)
        if parsed is None:
            # fallback: put whole content into summary
            logger.warning("Could not parse JSON from model output. Falling back to raw text as summary.")
            return {"summary": content, "keywords": [], "selling_points": []}

        # Ensure keys exist
        return {
            "summary": parsed.get("summary", ""),
            "keywords": parsed.get("keywords", []) or [],
            "selling_points": parsed.get("selling_points", []) or [],
        }

    def _extract_json(self, text: str) -> dict | None:
        """
        Try to robustly extract JSON blob from model text.
        """
        # Try direct JSON first
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try to find the first {...} block
        m = re.search(r"\{(?:.|\n)*\}", text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass

        # nothing parsed
        return None

    def save_analysis(self, analysis: dict, path: str):
        """Save analysis dict to a JSON file (creates dirs if needed)."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        logger.info("Saved analysis to %s", path)

    def analyze_and_save(self, product, path: str) -> dict:
        """Convenience: analyze and save to path, return analysis dict."""
        analysis = self.analyze_product(product)
        self.save_analysis(analysis, path)
        return analysis
