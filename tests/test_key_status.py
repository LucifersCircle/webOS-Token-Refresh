import hashlib
import importlib
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

from cryptography.fernet import Fernet

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with patch.dict(os.environ, {'ENCRYPTION_KEY': Fernet.generate_key().decode()}):
    server = importlib.import_module('app')

KEY = 'Ab' * 32
KEY_HASH = hashlib.sha256(KEY.encode()).hexdigest()


class KeyStatusTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database = Path(self.directory.name) / 'keys.db'
        self.original_path = server.DB_FILE
        server.DB_FILE = str(self.database)
        self.addCleanup(setattr, server, 'DB_FILE', self.original_path)
        server.initialize_db()
        self.client = server.app.test_client()

    def status(self, key_hash=KEY_HASH):
        return self.client.post('/api/key-status', data={'key_hash': key_hash})

    def manage(self, action):
        return self.client.post('/', data={'key': KEY, 'action': action}, headers={'Accept': 'application/json'})

    def test_absent_hash_is_false_and_lookup_does_not_insert(self):
        response = self.status()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'registered': False})
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        with sqlite3.connect(self.database) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM keys').fetchone()[0], 0)

    def test_status_tracks_existing_add_duplicate_and_remove_contract(self):
        self.assertEqual(self.manage('add').status_code, 201)
        before = self.database.read_bytes()
        self.assertEqual(self.status().json, {'registered': True})
        self.assertEqual(self.status(KEY_HASH.upper()).json, {'registered': True})
        self.assertEqual(self.database.read_bytes(), before)
        self.assertEqual(self.manage('add').status_code, 409)
        self.assertEqual(self.manage('remove').status_code, 200)
        self.assertEqual(self.status().json, {'registered': False})
        self.assertEqual(self.manage('remove').status_code, 404)

    def test_status_returns_only_registration_and_no_token_or_hash(self):
        self.manage('add')
        response = self.status()
        self.assertEqual(set(response.json), {'registered'})
        self.assertNotIn(KEY, response.get_data(as_text=True))
        self.assertNotIn(KEY_HASH, response.get_data(as_text=True))

    def test_invalid_hashes_are_rejected(self):
        for value in ['', 'a' * 63, 'g' * 64, 'a' * 65, "' OR 1=1 --"]:
            with self.subTest(value=value):
                self.assertEqual(self.status(value).status_code, 400)
        self.assertEqual(self.client.post('/api/key-status').status_code, 400)

    def test_missing_database_reports_unavailable_without_creating_it(self):
        server.DB_FILE = str(Path(self.directory.name) / 'missing.db')
        response = self.status()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('registered', response.json)
        self.assertFalse(Path(server.DB_FILE).exists())

    def test_unavailable_schema_does_not_claim_the_hash_is_absent(self):
        with sqlite3.connect(self.database) as conn:
            conn.execute('DROP TABLE keys')
        self.assertEqual(self.status().status_code, 503)

    def test_hash_lookup_requires_post(self):
        self.assertEqual(self.client.get('/api/key-status').status_code, 405)


if __name__ == '__main__':
    unittest.main()
