import os
import re
import sqlite3
import hashlib

from flask import Flask, request, jsonify, render_template_string
from cryptography.fernet import Fernet

app = Flask(__name__)

# Get encryption key from environment variable
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    raise Exception("ENCRYPTION_KEY is not set")

cipher = Fernet(encryption_key.encode())

# Database file path
DB_FILE = '/usr/src/app/db/keys.db'

# Function to initialize the database if it doesn't exist
def initialize_db():
    print(f"Initializing database at: {DB_FILE}", flush=True)
    if os.path.exists(DB_FILE) and not os.path.isfile(DB_FILE):
        print(f"Error: {DB_FILE} exists but is not a file and cannot be removed automatically.", flush=True)
        print("Please remove it manually and restart the application.", flush=True)
        return

    if not os.path.exists(DB_FILE):
        print(f"Database file does not exist. Creating a new one at: {DB_FILE}", flush=True)
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encrypted_key BLOB NOT NULL,
            key_hash TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized successfully.", flush=True)
    except Exception as e:
        print(f"Error initializing database: {e}", flush=True)

# HTML template for the landing page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebOS-TR</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #1a1a1a;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .container {
            text-align: center;
            width: 400px;
            margin: 0 auto; /* Center the container */
        }
        input {
            padding: 10px;
            margin: 10px 2px 10px 0;
            width: 300px;
            border-radius: 5px;
            border: 1px solid #444;
            background-color: #333;
            color: white;
            text-align: center;
            line-height: 1.5;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #5c6bc0;
            color: white;
            cursor: pointer;
            margin: 2px;
        }
        button:hover {
            background-color: #3f4c8c;
        }
        button.remove {
            background-color: #d9534f; /* Soft red */
        }
        button.remove:hover {
            background-color: #c9302c; /* Slightly darker red */
        }
        .message {
            margin: 10px auto;
            padding: 10px;
            background-color: #2e2e2e;
            border-radius: 5px;
            color: lightgreen;
            width: 100%; /* Match container width */
            text-align: center;
        }
        .message.duplicate,
        .message.not-found {
            color: yellow;
        }
        .message.invalid {
            color: red;
        }
        .description {
            margin-top: 15px;
            font-size: 14px;
            color: #ccc;
            text-align: center;
        }
        .footer {
            position: absolute;
            bottom: 10px;
            font-size: 14px;
            color: #777;
        }
        .footer a {
            color: #5c6bc0;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WebOS Token Refresher</h1>
        <form action="/" method="post">
            <input type="text" name="key" placeholder="Enter your token" required>
            <button type="submit" name="action" value="add">Add Token</button>
            <button type="submit" name="action" value="remove" class="remove">Remove Token</button>
        </form>
        {% if message %}
        <div class="message 
            {% if 'duplicate' in message %}duplicate{% endif %}
            {% if 'invalid token format' in message %}invalid{% endif %}
            {% if 'not found in database' in message %}not-found{% endif %}
        ">{{ message }}</div>
        {% endif %}

        <p class="description">
            This page allows you to securely add or remove your developer mode session token for LG WebOS. Tokens are hashed, encrypted, stored, and periodically refreshed with the LG Developer API to keep your session active.
        </p>
    </div>
    <div class="footer">
        <p>Check out the source code on <a href="https://github.com/LucifersCircle/webOS-Token-Refresh" target="_blank">GitHub</a>.</p>
    </div>
</body>
</html>
"""

# Landing page route
@app.route('/', methods=['GET', 'POST'])
def manage_key():
    message = None
    is_api_request = request.headers.get('Accept') == 'application/json'

    if request.method == 'POST':
        key = request.form.get('key')
        action = request.form.get('action')

        if not key:
            if is_api_request:
                return jsonify({'error': 'token is required'}), 400
            message = "token is required"
            return render_template_string(HTML_TEMPLATE, message=message)

        # Validate the key format
        if not re.fullmatch(r'^[a-fA-F0-9]{64}$', key):
            if is_api_request:
                return jsonify({'error': 'invalid token format - accepts 64-character alphanumeric tokens'}), 400
            message = "invalid token format - accepts 64-character alphanumeric tokens"
            return render_template_string(HTML_TEMPLATE, message=message)

        try:
            key_hash = hashlib.sha256(key.encode()).hexdigest()
            conn = sqlite3.connect(DB_FILE)

            if action == 'add':
                cursor = conn.execute("SELECT COUNT(*) FROM keys WHERE key_hash = ?", (key_hash,))
                if cursor.fetchone()[0] > 0:
                    conn.close()
                    if is_api_request:
                        return jsonify({'error': 'duplicate token hash detected - rejecting'}), 409
                    message = "duplicate token hash detected - rejecting"
                    return render_template_string(HTML_TEMPLATE, message=message)

                encrypted_key = cipher.encrypt(key.encode())
                conn.execute('INSERT INTO keys (encrypted_key, key_hash) VALUES (?, ?)', (encrypted_key, key_hash))
                conn.commit()
                conn.close()
                if is_api_request:
                    return jsonify({'message': 'token added successfully'}), 201
                message = "token added successfully"
                return render_template_string(HTML_TEMPLATE, message=message)

            elif action == 'remove':
                cursor = conn.execute("SELECT COUNT(*) FROM keys WHERE key_hash = ?", (key_hash,))
                if cursor.fetchone()[0] == 0:
                    conn.close()
                    if is_api_request:
                        return jsonify({'error': 'token hash not found in database'}), 404
                    message = "token hash not found in database"
                    return render_template_string(HTML_TEMPLATE, message=message)

                conn.execute("DELETE FROM keys WHERE key_hash = ?", (key_hash,))
                conn.commit()
                conn.close()
                if is_api_request:
                    return jsonify({'message': 'token removed successfully'}), 200
                message = "token removed successfully"
                return render_template_string(HTML_TEMPLATE, message=message)

            else:
                if is_api_request:
                    return jsonify({'error': 'invalid action'}), 400
                message = "invalid action"
                return render_template_string(HTML_TEMPLATE, message=message)

        except Exception as e:
            print(f"Error managing key: {e}", flush=True)
            if is_api_request:
                return jsonify({'error': str(e)}), 500
            message = f"an error occurred: {e}"
            return render_template_string(HTML_TEMPLATE, message=message)

    # Render HTML for GET requests
    return render_template_string(HTML_TEMPLATE, message=message)



if __name__ == '__main__':
    initialize_db() # Initialize database on startup
    app.run(host='0.0.0.0', port=5000)
