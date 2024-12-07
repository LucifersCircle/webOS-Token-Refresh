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

def remove_duplicates():
    """Remove duplicate keys from the database."""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Fetch all keys and normalize them
        cursor.execute("SELECT rowid, encrypted_key FROM keys")
        rows = cursor.fetchall()

        # Use a set to track normalized keys and find duplicates
        unique_keys = set()
        duplicates = []
        for rowid, encrypted_key in rows:
            # Normalize key by stripping whitespace and converting to lowercase
            normalized_key = encrypted_key.strip().lower()  # Adjust normalization as needed
            if normalized_key in unique_keys:
                duplicates.append(rowid)  # Track duplicate row IDs
            else:
                unique_keys.add(normalized_key)

        # Remove duplicates by rowid
        for rowid in duplicates:
            cursor.execute("DELETE FROM keys WHERE rowid = ?", (rowid,))

        conn.commit()
        conn.close()

        print(f"Removed {len(duplicates)} duplicate keys from the database.", flush=True)
    except Exception as e:
        print(f"Error removing duplicates: {e}", flush=True)



def fetch_keys():
    """Fetch and decrypt all keys from the database."""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.execute("SELECT encrypted_key FROM keys")
        # Decrypt each key before returning
        keys = [cipher.decrypt(row[0]).decode() for row in cursor.fetchall()]
        conn.close()
        print(f"Fetched and decrypted {len(keys)} keys from the database.", flush=True)
        return keys
    except Exception as e:
        print(f"Error fetching keys: {e}", flush=True)
        return []

def send_request(token):
    """Send the request to the API using the token."""
    url = f"{base_url}{token}"
    try:
        response = requests.get(url)
        masked_token = mask_token(token)
        print(f"Request to {masked_token} returned status code {response.status_code}.", flush=True)
    except requests.RequestException as e:
        print(f"Failed to send request for token {mask_token(token)}: {e}", flush=True)

if __name__ == "__main__":
    print("Starting task_runner...", flush=True)
    while True:
        # Remove duplicates before processing
        remove_duplicates()
        
        # Fetch keys and process them
        keys = fetch_keys()
        if not keys:
            print("No keys found in the database.", flush=True)
        for key in keys:
            send_request(key)
        
        # Wait before the next iteration
        print(f"Sleeping for {interval} seconds.", flush=True)
        time.sleep(interval)
