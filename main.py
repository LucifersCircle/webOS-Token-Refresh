import os
import time
import logging
import requests

# Configure logging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "https://developer.lge.com/secure/ResetDevModeSession.dev?sessionToken="
token = os.getenv('SESSION_TOKEN')
if not token:
    logging.error("SESSION_TOKEN is not set. Please set it in the environment variables.")
    exit(1)

interval = int(os.getenv('SCRIPT_INTERVAL', 86400))  # Default to 24 hours if not set.

def mask_token(url, token):
    """Masks the token in the URL, showing only the last 4 characters."""
    masked_token = "***" + token[-4:]
    return url.replace(token, masked_token)

def run_task():
    url = f"{base_url}{token}"
    try:
        response = requests.get(url)
        censored_url = mask_token(url, token)
        logging.info(f"Fired request to: {censored_url}")
        logging.info(f"Response Status Code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")

if __name__ == "__main__":
    while True:
        run_task()
        time.sleep(interval)
