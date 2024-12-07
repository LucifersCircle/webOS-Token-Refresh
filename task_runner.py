import os
import time
import sqlite3
import requests
from cryptography.fernet import Fernet

# Base configuration
base_url = "https://developer.lge.com/secure/ResetDevModeSession.dev?sessionToken="
interval = int(os.getenv('SCRIPT_INTERVAL', 86400))  # Default to 24 hours if not set
db_file = '/usr/src/app/db/keys.db'

# Load encryption key
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    raise RuntimeError("ENCRYPTION_KEY environment variable is not set.")
cipher = Fernet(encryption_key.encode())

def mask_token(token):
    """Masks the token, showing only the last 4 characters."""
    return f"***{token[-4:]}"

def fetch_keys():
    """Fetch and decrypt all keys from the database."""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.execute("SELECT encrypted_key FROM keys")
        # Decrypt each key before returning
        keys = [cipher.decrypt(row[0]).decode() for row in cursor.fetchall()]
        conn.close()
        print(f"Fetched and decrypted {len(keys)} keys from the database.")
        return keys
    except Exception as e:
        print(f"Error fetching keys: {e}")
        return []

def send_request(token):
    """Send the request to the API using the token."""
    url = f"{base_url}{token}"
    try:
        response = requests.get(url)
        masked_token = mask_token(token)
        print(f"Request to {masked_token} returned status code {response.status_code}.")
    except requests.RequestException as e:
        print(f"Failed to send request for token {mask_token(token)}: {e}")

if __name__ == "__main__":
    while True:
        keys = fetch_keys()
        if not keys:
            print("No keys found in the database.")
        for key in keys:
            send_request(key)
        print(f"Sleeping for {interval} seconds.")
        time.sleep(interval)
