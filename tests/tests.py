from django.test import TestCase
from django.contrib.auth import get_user_model

from speedtests.utils import generate_token


class ClientTestCase(TestCase):
    @staticmethod
    def create_user(name, email, password, is_superuser=False):
        User = get_user_model()
        token = generate_token()
        if is_superuser:
            create = User.objects.create_superuser
        else:
            create = User.objects.create_user
        user = create(username=name, email=email, password=password)
        user.token = token
        user.save()

    @classmethod
    def setUpTestData(cls):
        cls.create_user("admin", "admin@bench.im", "password0", True)
        cls.create_user("user1", "user1@bench.im", "password1")
        cls.create_user("user2", "user2@bench.im", "password2")

    def test_search_server(self):
        r = self.client.get("/api/search/", {"type": "server", "query": 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 0)
