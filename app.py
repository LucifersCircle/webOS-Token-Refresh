import os
import sqlite3
import base64
from flask import Flask, request, jsonify
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
