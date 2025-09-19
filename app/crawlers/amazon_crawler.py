import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import Session
from models.product import Product
import re
import pandas as pd
from database.session import SessionLocal


class AmazonCrawler:
    def __init__(self, user_agent: str = None):
        self.headers = {
            "User-Agent": user_agent
            or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def import_products_from_csv(self, csv_path: str):
        """Đọc file CSV và lưu toàn bộ sản phẩm vào DB"""
        df = pd.read_csv(csv_path)
        db = SessionLocal()

        urls = []
        for url in df["url"]:
            print(f"🔍 Đang crawl: {url}")
            data = self.scrape_product(url)
            if data:
                product = self.save_to_db(db, data)
                print(f"✅ Lưu thành công: {product.title} ({product.asin})")
                urls.append(url)
            else:
                print(f"⚠️ Không lấy được dữ liệu cho {url}")

        db.close()
        return urls

    def extract_asin(self, url: str) -> str:
        """Lấy ASIN từ URL Amazon"""
        match = re.search(r"/dp/([A-Z0-9]{10})", url)
        return match.group(1) if match else None

    def extract_affiliate_tag(self, url: str) -> str:
        """Lấy affiliate tag từ URL (nếu có)."""
        query = parse_qs(urlparse(url).query)
        return query.get("tag", [None])[0]

    def clean_price(self, price_str: str) -> float | None:
        if not price_str:
            return None
        cleaned = price_str.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None

    def clean_rating(self, rating_str: str) -> float | None:
        if not rating_str:
            return None
        match = re.match(r"([0-9.]+)", rating_str)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def scrape_product(self, url: str) -> dict | None:
        """Crawl dữ liệu sản phẩm Amazon"""
        asin = self.extract_asin(url)
        affiliate_tag = self.extract_affiliate_tag(url)

        try:
            r = requests.get(url, headers=self.headers, timeout=15)
            if r.status_code != 200:
                print(f"❌ Lỗi HTTP {r.status_code} cho URL: {url}")
                return None

            soup = BeautifulSoup(r.text, "html.parser")

            # Title
            title = soup.select_one("#productTitle")
            title = title.get_text(strip=True) if title else None

            # Price
            price = soup.select_one(".a-price .a-offscreen")
            price = self.clean_price(price.get_text(strip=True) if price else None)

            # Rating
            rating = soup.select_one("span[data-asin] span.a-icon-alt") \
                  or soup.select_one("i.a-icon-star span.a-icon-alt")
            rating = self.clean_rating(rating.get_text(strip=True) if rating else None)

            # Image
            image = soup.select_one("#landingImage")
            image = image["src"] if image else None

            return {
                "asin": asin,
                "title": title or "(No title)",
                "price": price,
                "rating": rating,
                "image": image,
                "url": url,
                "affiliate_tag": affiliate_tag,
            }
        except Exception as e:
            print(f"⚠️ Lỗi khi crawl {url}: {e}")
            return None

    def save_to_db(self, session: Session, data: dict):
        if not data or not data.get("asin"):
            return None

        product = session.query(Product).filter_by(asin=data["asin"]).first()
        if product:
            # update
            product.title = data["title"]
            product.price = data["price"]
            product.rating = data["rating"]
            product.url = data["url"]
            product.image = data["image"]
            product.affiliate_tag = data["affiliate_tag"]
        else:
            # insert mới
            product = Product(**data)
            session.add(product)

        session.commit()
        return product


if __name__ == "__main__":
    crawler = AmazonCrawler()
    urls = crawler.import_products_from_csv("data/affiliate_amazone.csv")
    print(f"👉 Đã crawl xong {len(urls)} sản phẩm.")
