import os
import json
import logging
from app import get_db
from app.services.analyzer_service import AnalyzerService
from app.services.script_service import ScriptService
from app.models.product import Product

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_tool():
    db = next(get_db())
    products = db.query(Product).all()

    if not products:
        print("⚠️ Không có sản phẩm nào trong DB. Hãy crawl trước!")
        return

    product = products[0]
    print(f"🔍 Đang xử lý sản phẩm: {product.title} ({getattr(product, 'asin', 'N/A')})")

    # --- 1. Phân tích sản phẩm ---
    analyzer = AnalyzerService()
    analysis_file = f"app/data/analysis_{getattr(product, 'asin', 'unknown')}.json"
    analysis = analyzer.analyze_and_save(product, analysis_file)
    print(f"✅ Phân tích đã lưu: {analysis_file}")

    # --- 2. Sinh kịch bản ---
    script_service = ScriptService()
    script_text = script_service.generate_script(analysis, product=product)
    script_file = f"app/data/script_{getattr(product, 'asin', 'unknown')}.txt"
    script_service.save_script(script_file, script_text)
    print(f"✅ Kịch bản đã lưu: {script_file}")

    # --- 3. Sinh audio (TTS) ---
    # TODO: Tích hợp TTSService
    # audio_file = TTSService().generate_audio(script_file)

    # --- 4. Sinh video ---
    # TODO: Tích hợp VideoService
    # video_file = VideoService().generate_video(audio_file, product.image)

    print("🎬 Pipeline hoàn tất!")


if __name__ == "__main__":
    run_tool()
