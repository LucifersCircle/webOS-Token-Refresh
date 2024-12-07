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
    print(f"Initializing database at: {DB_FILE}")
    if os.path.exists(DB_FILE) and not os.path.isfile(DB_FILE):
        print(f"Error: {DB_FILE} exists but is not a file and cannot be removed automatically.")
        print("Please remove it manually and restart the application.")
        return

    if not os.path.exists(DB_FILE):
        print(f"Database file does not exist. Creating a new one at: {DB_FILE}")
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
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize database on startup
initialize_db()

# HTML template for the landing page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Key Management</title>
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
        }
        input {
            padding: 10px;
            margin: 10px 0;
            width: 300px;
            border-radius: 5px;
            border: 1px solid #444;
            background-color: #333;
            color: white;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #5c6bc0;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #3f4c8c;
        }
        form {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Key Management</h1>
        <form action="/add_key" method="post">
            <input type="text" name="key" placeholder="Enter your key to add" required>
            <button type="submit">Add Key</button>
        </form>
        <form action="/remove_key" method="post">
            <input type="text" name="key" placeholder="Enter your key to remove" required>
            <button type="submit">Remove Key</button>
        </form>
    </div>
</body>
</html>
"""

# New route to handle key removal
@app.route('/remove_key', methods=['POST'])
def remove_key():
    key = request.form.get('key')
    if not key:
        return jsonify({'error': 'Key is required'}), 400

    # Validate the key using a regular expression
    if not re.fullmatch(r'^[a-fA-F0-9]{64}$', key):
        return jsonify({'error': 'Invalid key format. Only 64-character alphanumeric keys are allowed.'}), 400

    try:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        conn = sqlite3.connect(DB_FILE)
        
        # Check if the key exists
        cursor = conn.execute("SELECT COUNT(*) FROM keys WHERE key_hash = ?", (key_hash,))
        if cursor.fetchone()[0] == 0:
            conn.close()
            return jsonify({'error': 'Key not found'}), 404

        # Remove the key from the database
        conn.execute("DELETE FROM keys WHERE key_hash = ?", (key_hash,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Key removed successfully'}), 200
    except Exception as e:
        print(f"Error removing key: {e}")
        return jsonify({'error': str(e)}), 500

# Landing page route
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# Add key route
@app.route('/add_key', methods=['POST'])
def add_key():
    key = request.form.get('key')
    if not key:
        return jsonify({'error': 'Key is required'}), 400

    # Validate the key using a regular expression
    if not re.fullmatch(r'^[a-fA-F0-9]{64}$', key):
        return jsonify({'error': 'Invalid key format. Only 64-character alphanumeric keys are allowed.'}), 400

    try:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        encrypted_key = cipher.encrypt(key.encode())
        conn = sqlite3.connect(DB_FILE)
        
        # Check for duplicate hash
        cursor = conn.execute("SELECT COUNT(*) FROM keys WHERE key_hash = ?", (key_hash,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'error': 'Duplicate key detected'}), 409

        conn.execute('INSERT INTO keys (encrypted_key, key_hash) VALUES (?, ?)', (encrypted_key, key_hash))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Key added successfully'}), 201
    except Exception as e:
        print(f"Error adding key: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
