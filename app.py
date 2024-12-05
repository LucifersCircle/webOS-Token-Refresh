import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string
from cryptography.fernet import Fernet

app = Flask(__name__)

# Get encryption key from environment variable
encryption_key = os.getenv('ENCRYPTION_KEY')
if not encryption_key:
    raise Exception("ENCRYPTION_KEY is not set")

cipher = Fernet(encryption_key.encode())

# Database file path
DB_FILE = 'keys.db'

# Function to initialize the database if it doesn't exist
def initialize_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        conn.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            encrypted_key BLOB NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized")

# Initialize database on startup
initialize_db()

# HTML template for the landing page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Key</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Add a Key</h1>
        <form action="/add_key" method="post">
            <input type="text" name="key" placeholder="Enter your key" required>
            <button type="submit">Submit</button>
        </form>
    </div>
</body>
</html>
"""

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
    try:
        encrypted_key = cipher.encrypt(key.encode())
        conn = sqlite3.connect(DB_FILE)
        conn.execute('INSERT INTO keys (encrypted_key) VALUES (?)', (encrypted_key,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Key added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
