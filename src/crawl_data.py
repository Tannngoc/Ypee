import requests
import csv
import time

def fetch_tiki_products(keyword, limit=50, pages=1):
    base_url = "https://tiki.vn/api/v2/products"
    all_products = []

    for page in range(1, pages + 1):
        params = {
            "limit": limit,
            "page": page,
            "q": keyword
        }
        res = requests.get(base_url, params=params, headers={
            "User-Agent": "Mozilla/5.0"
        })
        if res.status_code != 200:
            print(f"⚠️ Request lỗi: {res.status_code}")
            continue

        data = res.json()
        products = data.get("data", [])
        for p in products:
            all_products.append({
                "name": p.get("name", ""),
                "price": p.get("price", 0),
                "rating": p.get("rating_average", 0),
                "reviews": p.get("review_count", 0),
                "image": p.get("thumbnail_url", ""),
                "link": f"https://tiki.vn/{p.get('url_path', '')}"
            })

        time.sleep(1)

    return all_products


def save_to_csv(products, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)


if __name__ == "__main__":
    keyword = "tai nghe bluetooth"
    print(f"🔍 Đang crawl sản phẩm Tiki cho từ khoá: {keyword}")
    products = fetch_tiki_products(keyword, limit=24, pages=2)

    if products:
        save_to_csv(products, "data/tiki_products.csv")
        print(f"✅ Đã lưu {len(products)} sản phẩm vào tiki_products.csv")
    else:
        print("🚫 Không lấy được sản phẩm nào")
