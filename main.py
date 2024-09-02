import os
import time
import logging
import requests

# Configure logging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_url = "https://developer.lge.com/secure/ResetDevModeSession.dev?sessionToken="
token = os.getenv('SESSION_TOKEN')
interval = int(os.getenv('SCRIPT_INTERVAL', 86400))  # In seconds. Default 24 hours.

def mask_token(url, token):
    # Return the URL with the token censored.
    return url.replace(token, "<TOKEN_CENSORED>")

def run_task():
    url = f"{base_url}{token}"
    try:
        response = requests.get(url)
        # Mask the token in the URL for logging.
        censored_url = mask_token(url, token)
        logging.info(f"Fired request to: {censored_url} at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Response Status Code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    while True:
        run_task()
        time.sleep(interval)
