from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd


url = "https://books.toscrape.com/"

response = requests.get(url)
response.encoding = response.apparent_encoding

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

books = soup.select("article.product_pod")

data = []

for book in books:
    title = book.h3.a["title"]
    price_text = book.select_one(".price_color").text.strip()
    price = float(price_text.replace("£", "").replace("Â", "").strip())
    availability = book.select_one(".availability").text.strip()

    data.append({
        "title": title,
        "price": price,
        "availability": availability,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

df = pd.DataFrame(data)

print(df)

import sqlite3

conn = sqlite3.connect("price_tracker.db")

df.to_sql(
    "products",
    conn,
    if_exists="append",
    index=False
)

conn.close()

print("Data saved to database!")

import sqlite3

conn = sqlite3.connect("price_tracker.db")

query = """
SELECT title, price, availability
FROM products
LIMIT 5
"""

result = pd.read_sql_query(query, conn)

print("\nData from SQLite:")
print(result)

conn.close()
