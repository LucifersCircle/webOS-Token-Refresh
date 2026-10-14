
# WebOS Token Refresher

A secure web-based tool for refreshing LG WebOS developer mode session tokens. This project ensures your tokens are stored securely and refreshes them periodically with the LG Developer API.

---

## Features

- **Web Interface**
- **API for CLI calls**
- **Automated Refresh**:
  - Periodically refreshes stored tokens with the LG Developer API.
- **Security**:
  - Tokens are hashed using SHA-256 to ensure uniqueness without storing plaintext. This is used to reject duplicate entries, and to allow deletion of your token.
  - Encrypted tokens are stored securely using an environment-provided encryption key.
  - No Ads
  - Open Source

---

## Instances

Anyone can run an instance for this, although I'm not sure why anybody would really want to. However, if you decide to and want to share it then make a PR and add it here.

- **[https://lg.pirate.vodka](https://lg.pirate.vodka)**

---

## Usage

### Add a Token
1. Web UI ([lg.pirate.vodka](https://lg.pirate.vodka))
2. API via `curl`
 
**Command:**
```bash
curl -X POST -d "key=YOUR_TOKEN_HERE&action=add" -H "Accept: application/json" https://lg.pirate.vodka
```

### Remove a Token
1. Web UI ([lg.pirate.vodka](https://lg.pirate.vodka))
2. API via `curl`

**Command:**
```bash
curl -X POST -d "key=YOUR_TOKEN_HERE&action=remove" -H "Accept: application/json" https://lg.pirate.vodka
```

---

### Check Token Registration

Compute the SHA-256 digest of the exact trimmed token, preserving its letter case,
and submit only that digest to the read-only status endpoint:

```bash
curl -X POST -d "key_hash=SHA256_DIGEST" -H "Accept: application/json" https://lg.pirate.vodka/api/key-status
```

A valid hash returns HTTP 200 with `{"registered": true}` when it is present in
the database, or `{"registered": false}` when it is absent. Invalid hashes return
400; an unavailable database returns 503. Responses use `Cache-Control: no-store`.
The lookup does not insert, remove, refresh, or decrypt a token.

Run the API regression checks with Flask and cryptography installed:

```bash
python -m unittest discover -s tests -v
```

## Requirements

- **Docker**
- **Docker Compose**
- An active LG WebOS developer account.

---

## Deployment

### 0. Provided Docker compose file

### 1. Clone the repository:
```bash
git clone https://github.com/LucifersCircle/webOS-Token-Refresh.git
cd webOS-Token-Refresh
```

### 2. Configure environment variables in `.env`:
- `ENCRYPTION_KEY`: A secure encryption key for token storage.
- `SCRIPT_INTERVAL`: (Optional) Interval for the task runner to refresh tokens, in seconds (default: 86400).
- `source: /path/to/db/dir`: Add the directory you want to store keys.db inside. `Ex. /home/username/db`

### 3. Build and start the application:
```bash
docker-compose up --build
```

### 4. Access the web interface:

Navigate to `http://localhost:5000` in your browser.

---

## Development Notes

### Tech Stack:
- Python (Flask)
- SQLite
- Gunicorn (production server)
- Docker

### Logs:

- Application and task runner logs are accessible via Docker.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

---

## License

This project is licensed under the GPL-3.0 License. See `LICENSE` for details.

---
