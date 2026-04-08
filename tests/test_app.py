import json
import unittest
from pathlib import Path

from app import app, ensure_upload_folder


class AppRoutesTestCase(unittest.TestCase):
    def setUp(self):
        ensure_upload_folder()
        self.client = app.test_client()
        self.fixture = Path(app.config["UPLOAD_FOLDER"]) / "fixture_test.txt"
        self.fixture.write_text("banana banana bandana", encoding="utf-8")

    def tearDown(self):
        if self.fixture.exists():
            self.fixture.unlink()

    def test_algorithms_route(self):
        response = self.client.get("/algorithms")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("kmp", data)

    def test_search_route(self):
        response = self.client.post(
            "/search",
            data=json.dumps({"pattern": "ana", "algorithm": "kmp", "files": [self.fixture.name]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["results"][0]["occurrences"], [1, 3, 8, 10, 18])

    def test_step_route(self):
        response = self.client.post(
            "/step",
            data=json.dumps({"pattern": "ana", "algorithm": "boyer_moore", "file": self.fixture.name}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("steps", payload)
        self.assertTrue(len(payload["steps"]) > 0)


if __name__ == "__main__":
    unittest.main()
