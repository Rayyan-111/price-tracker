import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("\n========== PRICE TRACKER RUN ==========\n")

print("1. Scraping prices...")
subprocess.run(
    [sys.executable, str(BASE_DIR / "scraper.py")],
    check=True
)

print("\n2. Checking price drops...")
subprocess.run(
    [sys.executable, str(BASE_DIR / "tracker.py")],
    check=True
)

print("\n========== RUN COMPLETE ==========\n") 