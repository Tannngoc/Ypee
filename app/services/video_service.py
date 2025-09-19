import os
import time
import requests
from openai import OpenAI
from dotenv import load_dotenv
from database.session import SessionLocal
from models.product import Product

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VIDEOGEN_API_KEY = os.getenv("VIDEOGEN_API_KEY")

# OpenAI client để sinh script
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(product: Product) -> str:
    prompt = f"""
    Viết nội dung video quảng cáo sản phẩm {product.title}.  
    - Nêu các đặc điểm nổi bật của sản phẩm  
    - Kèm lời kêu gọi hành động: "Mua ngay tại link bên dưới"
    """
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

def create_videogen_task(script: str, image_url: str = None) -> str:
    """Gửi request preview tạo video và trả về task ID"""
    url = "https://ext.videogen.io/v2/prompt-to-video"  # hoặc script-to-video endpoint nếu có
    headers = {
        "Authorization": f"Bearer {VIDEOGEN_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": script,
        # nếu muốn có image làm background hoặc làm khung đầu hoặc tham chiếu media
        "backgroundImageUrls": [image_url] if image_url else None,
        # có thể có các tùy chọn như voice, fonts nếu API hỗ trợ
    }
    # loại bỏ các trường None
    clean_payload = {k: v for k, v in payload.items() if v is not None}
    resp = requests.post(url, headers=headers, json=clean_payload)
    resp.raise_for_status()
    data = resp.json()
    api_file_id = data.get("apiFileId")
    return api_file_id

def poll_videogen_task(api_file_id: str, timeout: int = 300, interval: int = 10) -> str:
    """Poll tới khi video hoàn thành, rồi trả link tải file video"""
    url = "https://ext.videogen.io/v2/get-file"
    headers = {
        "Authorization": f"Bearer {VIDEOGEN_API_KEY}"
    }
    params = {"apiFileId": api_file_id}
    elapsed = 0
    while elapsed < timeout:
        time.sleep(interval)
        elapsed += interval
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        status = data.get("status")
        print(f"[VideoGen] Task {api_file_id} status: {status}")
        if status == "Success":
            file_url = data.get("file", {}).get("fileUrl") or data.get("signedUrl") or data.get("apiFileSignedUrl")
            return file_url
        elif status == "Fail":
            raise Exception(f"VideoGen task failed: {data}")
    raise TimeoutError("VideoGen task did not finish in time")

def pipeline_for_product(product: Product):
    script = generate_script(product)
    # Optionally sinh voice nếu muốn
    # audio_path = ...  
    api_id = create_videogen_task(script, image_url=product.image)
    print(f"🚀 VideoGen task created: {api_id}")
    file_url = poll_videogen_task(api_id)
    print(f"✅ Video ready at {file_url}")
    # Tải video
    local_path = f"output/{product.asin}.mp4"
    video_resp = requests.get(file_url)
    video_resp.raise_for_status()
    with open(local_path, "wb") as f:
        f.write(video_resp.content)
    print(f"📂 Video downloaded: {local_path}")
    return local_path

if __name__ == "__main__":
    db = SessionLocal()
    prods = db.query(Product).filter(Product.image.isnot(None)).all()
    for p in prods:
        print(f"Processing product {p.asin}")
        try:
            video_file = pipeline_for_product(p)
            # sau đó call youtube upload với video_file, title, description chứa p.url affiliate link
        except Exception as e:
            print(f"Error for product {p.asin}: {e}")
    db.close()
