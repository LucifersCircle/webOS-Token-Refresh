import os
import sqlite3
import logging
import requests
from cryptography.fernet import Fernet
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get encryption key from environment variable
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    raise Exception("ENCRYPTION_KEY is not set")

cipher = Fernet(encryption_key.encode())
base_url = "https://developer.lge.com/secure/ResetDevModeSession.dev?sessionToken="
interval = int(os.getenv('SCRIPT_INTERVAL', 86400))  # Default to 24 hours

def run_task():
    conn = sqlite3.connect('keys.db')
    cursor = conn.execute('SELECT encrypted_key FROM keys')
    encrypted_keys = cursor.fetchall()
    conn.close()

    for encrypted_key in encrypted_keys:
        try:
            decrypted_key = cipher.decrypt(encrypted_key[0]).decode()
            url = f"{base_url}{decrypted_key}"
            response = requests.get(url)
            logging.info(f"Fired request to: {url[-8:]}")
            logging.info(f"Response Status Code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error processing key: {e}")

if __name__ == "__main__":
    while True:
        run_task()
        time.sleep(interval)
