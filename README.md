# WebOS Token Refresh Script

## Overview

This repository contains a Python script designed to periodically refresh a WebOS token by making HTTP requests to the LG Dev mode refresh URL (*https://developer.lge.com/secure/ResetDevModeSession.dev?sessionToken=*). The script is containerized using Docker and can be easily managed using Docker Compose.

## Features

- **Token Refresh**: The script sends an HTTP GET request to refresh the token.
- **Logging**: Logs include timestamps, request status, and a censored version of the URL to protect your token while viewing.
- **Environment Configuration**: Uses environment variables for configuration, making it easy to manage tokens and intervals.

## Docker Compose Configuration

The project includes a Docker Compose configuration for easy deployment. Below is the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  token-refresh:
    image: luciferscircle/webos-token-refresh
    container_name: WebOS-TR
    environment:
      - SESSION_TOKEN=Your_Token_Here
      - SCRIPT_INTERVAL=86400
    restart: always
```

### Configuration Details

- **`image:`** Specifies the Docker image to use from Docker Hub.
- **`container_name:`** Names the container `WebOS-TR`.
- **`environment:`**
  - `SESSION_TOKEN:` The token used for authentication. Replace `Your_Token_Here` with your actual token.
  - `SCRIPT_INTERVAL:` Interval (in seconds) at which the script should run. Default is 86400 seconds (24 hours).
- **`restart: always:`** Ensures the container restarts automatically if it stops.

## Python Script

The Python script `main.py` handles the token refresh logic. Below is the script:

```python
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
```

### Script Details

- **Logging Configuration**: Logs are set to `INFO` level with timestamps, and log messages include the request status and a censored URL.
- **Token Censorship**: The token in the URL is replaced with `<TOKEN_CENSORED>` for privacy.
- **Interval**: The script waits for a period defined by `SCRIPT_INTERVAL` before making the next request. Default is 24 hours (86400 seconds).

## How to Use

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/LucifersCircle/webOS-Token-Refresh.git
   cd repository
   ```

2. **Edit `docker-compose.yml`**: Replace `Your_Token_Here` with your actual session token.

3. **Start the Service**:
   ```bash
   docker-compose up -d
   ```

4. **Check Logs**:
   ```bash
   docker logs WebOS-TR
   ```

5. **Stop the Service**:
   ```bash
   docker-compose down
   ```
## CLI Instructions

Alternatively, you can run the Docker container from the DockerHub Image using the CLI. Follow these steps:

1. **Pull the Docker Image**:

   ```bash
   docker pull luciferscircle/webos-token-refresh
   ```

2. **Run the Docker Container** with environment variables:

   ```bash
   docker run -d --name WebOS-TR -e SESSION_TOKEN=Your_Token_Here -e SCRIPT_INTERVAL=86400 luciferscircle/webos-token-refresh
   ```

### CLI Options

- `-d`: Run the container in detached mode.
- `--name WebOS-TR`: Assign a name to the container.
- `-e SESSION_TOKEN=Your_Token_Here`: Set the session token environment variable.
- `-e SCRIPT_INTERVAL=86400`: Set the interval environment variable.

## Questions

If you have any questions or need further assistance, feel free to open an issue.