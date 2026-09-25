import sqlite3
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_telegram_alert(title, old_price, new_price, drop, drop_percent):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    message = f"""
🚨 PRICE DROP ALERT

Product: {title}

Old Price: £{old_price:.2f}
New Price: £{new_price:.2f}
Drop: £{drop:.2f}
Drop %: {drop_percent:.2f}%
"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message
        }
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)

def show_price_drop(title, old_price, new_price, drop, drop_percent):
    print("\n🚨 PRICE DROP ALERT")
    print("=" * 40)
    print(f"Product   : {title}")
    print(f"Old Price : £{old_price:.2f}")
    print(f"New Price : £{new_price:.2f}")
    print(f"Drop      : £{drop:.2f}")
    print(f"Drop %    : {drop_percent:.2f}%")
    print("=" * 40)

DB_NAME = "price_tracker.db"

# Connect to database
conn = sqlite3.connect(DB_NAME)

# Create alerts table
conn.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    old_price REAL,
    new_price REAL,
    drop_amount REAL,
    drop_percent REAL,
    sent_at TEXT
)
""")

conn.commit()

# Get all price history
query = """
SELECT
    title,
    price,
    availability,
    scraped_at
FROM products
ORDER BY title, scraped_at
"""


df = pd.read_sql_query(query, conn)

df["price"] = (
    df["price"]
    .astype(str)
    .str.replace("£", "", regex=False)
    .str.strip()
)

df["price"] = pd.to_numeric(df["price"], errors="coerce")


print("\nPRICE HISTORY")
print("=" * 70)

print(df.to_string(index=False))


# Check price drops
print("\n\nPRICE DROP CHECK")
print("=" * 70)


for title, group in df.groupby("title"):

    # Sort by time
    group = group.sort_values("scraped_at")

    # Need at least 2 records
    if len(group) < 2:
        continue

    old_price = group.iloc[-2]["price"]
    new_price = group.iloc[-1]["price"]


    if pd.isna(old_price) or pd.isna(new_price):
        continue

    if new_price < old_price:
        drop = old_price - new_price
        drop_percent = (drop / old_price) * 100

        if drop_percent >= 5:
            show_price_drop(
                title,
                old_price,
                new_price,
                drop,
                drop_percent
            )
            # Send alert only for a NEW price drop
            last_alert = conn.execute(
                """
                SELECT new_price
                FROM alerts
                WHERE title = ?
                ORDER BY sent_at DESC
                LIMIT 1
                """,
                (title,)
            ).fetchone()

            if last_alert is None or float(last_alert[0]) != float(new_price):
                send_telegram_alert(
                    title,
                    old_price,
                    new_price,
                    drop,
                    drop_percent
                )

                conn.execute(
                    """
                    INSERT INTO alerts
                    (title, old_price, new_price, drop_amount, drop_percent, sent_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                    """,
                    (title, old_price, new_price, drop, drop_percent)
                )

                conn.commit()

conn.close()
