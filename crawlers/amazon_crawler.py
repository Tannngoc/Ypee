import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re


class AmazonCrawler:
    def __init__(self, user_agent: str = None):
        self.headers = {
            "User-Agent": (
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

    def extract_asin(self, url: str) -> str:
        """
        Lấy ASIN từ URL Amazon.
        Ví dụ: https://www.amazon.com/.../dp/B0DWGX3WQC?... -> B0DWGX3WQC
        """
        match = re.search(r"/dp/([A-Z0-9]{10})", url)
        return match.group(1) if match else None

    def extract_affiliate_tag(self, url: str) -> str:
        """Lấy affiliate tag từ URL (nếu có)."""
        query = parse_qs(urlparse(url).query)
        return query.get("tag", [None])[0]

    def scrape_product(self, url: str) -> dict:
        """
        Crawl dữ liệu cơ bản của sản phẩm Amazon:
        - title
        - price
        - rating
        - image
        - asin
        - affiliate_tag
        """
        asin = self.extract_asin(url)
        affiliate_tag = self.extract_affiliate_tag(url)

        r = requests.get(url, headers=self.headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        title = soup.select_one("#productTitle")
        title = title.get_text(strip=True) if title else None

        # Price
        price = soup.select_one(".a-price .a-offscreen")
        price = price.get_text(strip=True) if price else None

        # Rating
        rating = soup.select_one("span[data-asin] span.a-icon-alt")
        if not rating:
            rating = soup.select_one("i.a-icon-star span.a-icon-alt")
        rating = rating.get_text(strip=True) if rating else None

        # Image
        image = soup.select_one("#landingImage")
        image = image["src"] if image else None

        return {
            "asin": asin,
            "title": title,
            "price": price,
            "rating": rating,
            "image": image,
            "url": url,
            "affiliate_tag": affiliate_tag,
        }


if __name__ == "__main__":
    crawler = AmazonCrawler()

    urls = [
        "https://www.amazon.com/Lee-Riker-Chukka-Honey-Chocolate/dp/B0DWGX3WQC?tag=luonglow07-20",
        "https://www.amazon.com/Owala-FreeSip-Insulated-Stainless-BPA-Free/dp/B0BZYCJK89?tag=luonglow07-20",
        "https://www.amazon.com/Mighty-Patch-Hydrocolloid-Absorbing-count/dp/B074PVTPBW?tag=luonglow07-20",
    ]

    for u in urls:
        data = crawler.scrape_product(u)
        print(data)
