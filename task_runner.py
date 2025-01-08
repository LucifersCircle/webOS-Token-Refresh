import os
import time
import sqlite3
from multiprocessing import Pool, cpu_count

import requests
from cryptography.fernet import Fernet

# Base configuration
base_url = "https://developer.lge.com/secure/ResetDevModeSession.dev?sessionToken="
interval = int(os.getenv('SCRIPT_INTERVAL', 86400))  # Default to 24 hours if not set
db_file = '/usr/src/app/db/keys.db'
batch_size = 100  # Number of keys to process in each batch

# Load encryption key
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    raise RuntimeError("ENCRYPTION_KEY environment variable is not set.")
cipher = Fernet(encryption_key.encode())

# Initialize database connection
def get_db_connection():
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}", flush=True)
        return None

# Fetch a batch of encrypted keys from the database
def fetch_encrypted_keys(offset, limit):
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_key FROM keys LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        print(f"Error fetching keys: {e}", flush=True)
        return []

# Decrypt a single key
def decrypt_key(encrypted_key):
    try:
        return cipher.decrypt(encrypted_key).decode()
    except Exception as e:
        print(f"Error decrypting key: {e}", flush=True)
        return None

# Send the request to the API using the token
def send_request(token):
    url = f"{base_url}{token}"
    try:
        response = requests.get(url)
        masked_token = mask_token(token)
        print(f"Request to {masked_token} returned status code {response.status_code}.", flush=True)
    except requests.RequestException as e:
        print(f"Failed to send request for token {mask_token(token)}: {e}", flush=True)

# Masks the token for logs, showing only the last 4 characters
def mask_token(token):
    return f"***{token[-4:]}"

# Process a batch of keys: decrypt and send requests
def process_keys_batch(encrypted_keys):
    with Pool(processes=cpu_count()) as pool:
        decrypted_keys = pool.map(decrypt_key, encrypted_keys)
    # Filter out any None values resulting from decryption errors
    valid_keys = [key for key in decrypted_keys if key is not None]
    for key in valid_keys:
        send_request(key)
    return len(valid_keys)

if __name__ == "__main__":
    print("Starting task_runner...", flush=True)
    while True:
        offset = 0
        total_processed = 0
        while True:
            encrypted_keys = fetch_encrypted_keys(offset, batch_size)
            if not encrypted_keys:
                break
            processed_count = process_keys_batch(encrypted_keys)
            total_processed += processed_count
            offset += batch_size
        print(f"Fetched, decrypted, and processed {total_processed} keys from the database.", flush=True)
        print(f"Sleeping for {interval} seconds.", flush=True)
        time.sleep(interval)
