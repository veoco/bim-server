from django.test import TestCase
from django.contrib.auth import get_user_model

from .utils import generate_token


class SpeedtestTestCase(TestCase):
    @classmethod
    def setUpTestData(self):
        User = get_user_model()
        token = generate_token()
        admin = User.objects.create_superuser(
            "admin", "admin@bench.im", "poiuy98765432"
        )
        admin.token = token
        admin.save()

    def test_search_server(self):
        r = self.client.get("/api/search/", {"type": "server", "query": 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 0)
