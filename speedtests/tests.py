from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Server
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

        s1 = Server(
            provider=Server.Provider.OOKLA,
            detail={
                "id": "234",
                "host": "speedtest-adl.cdn.on.net:8080",
                "name": "Adelaide",
                "sponsor": "Internode",
                "cc": "AU",
            },
        )
        s1.save()
        s2 = Server(
            provider=Server.Provider.OOKLA,
            detail={
                "id": "285",
                "host": "sp1.scinternet.net:8080",
                "name": "Cedar City, UT",
                "sponsor": "South Central Internet",
                "cc": "US",
            },
        )
        s2.save()

    def test_search_server(self):
        r = self.client.get("/api/search/", {"type": "server", "query": 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        r = self.client.get("/api/search/", {"type": "server", "query": 285})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        r = self.client.get("/api/search/", {"type": "server", "query": "Cedar"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        r = self.client.get("/api/search/", {"type": "server", "query": "Inter"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 2)
        
        r = self.client.get("/api/search/", {"type": "server", "query": "US"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

        r = self.client.get("/api/search/", {"type": "server", "query": "DE"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 0)
    
    def test_search_server_list(self):
        data = {
            "name": "test sl 1",
            "readme": "test server list one",
            "servers": [1],
        }
        r = self.client.post("/api/server_list/", data, content_type="application/json")
        self.assertEqual(r.status_code, 200)

        r = self.client.get("/api/search/", {"type": "server_list", "query": 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)

    def test_get_server_from_id(self):
        r = self.client.get("/api/server/", {"pk": 1})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["pk"], 1)

    def test_create_server_list(self):
        data = {
            "name": "test sl 1",
            "readme": "test server list one",
            "servers": [1],
        }
        r = self.client.post("/api/server_list/", data, content_type="application/json")
        self.assertEqual(r.status_code, 200)

        pk = r.json()["pk"]
        self.assertIsInstance(pk, int)

        r = self.client.get("/api/server_list/", {"pk": pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()['servers']), 1)

        data = {
            "name": "test sl 2",
            "readme": "test server list two",
            "servers": [1, 2],
        }
        r = self.client.post("/api/server_list/", data, content_type="application/json")
        self.assertEqual(r.status_code, 200)

        pk = r.json()["pk"]
        self.assertIsInstance(pk, int)

        r = self.client.get("/api/server_list/", {"pk": pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()['servers']), 2)
    
    def test_modify_server_list_servers(self):
        data = {
            "name": "test sl 1",
            "readme": "test server list one",
            "servers": [1],
        }
        r = self.client.post("/api/server_list/", data, content_type="application/json")

        target_pk = r.json()["pk"]
        target_data = {
            "pk": target_pk,
            "name": "test sl 1",
            "readme": "test add server",
            "servers": [1, 2],
        }
        r = self.client.post("/api/server_list/", target_data, content_type="application/json")
        self.assertEqual(r.status_code, 400)

        self.client.login(username="admin@bench.im", password="poiuy98765432")
        r = self.client.post("/api/server_list/", target_data, content_type="application/json")
        self.assertEqual(r.status_code, 200)

        pk = r.json()["pk"]
        r = self.client.get("/api/server_list/", {"pk": pk})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()['servers']), 2)

        target_data = {
            "pk": target_pk,
            "readme": "test server list without name",
            "servers": [1, 2],
        }
        r = self.client.post("/api/server_list/", target_data, content_type="application/json")
        self.assertEqual(r.status_code, 400)

        target_data = {
            "pk": target_pk,
            "name": "test sl 1 - test sl 1 - test sl 1 - test sl 1 - test sl 1 - test sl 1",
            "readme": "test server list name too long",
            "servers": [1, 2],
        }
        r = self.client.post("/api/server_list/", target_data, content_type="application/json")
        self.assertEqual(r.status_code, 400)

        target_data = {
            "pk": target_pk,
            "name": "test with empty readme",
            "readme": "",
            "servers": [1, 2],
        }
        r = self.client.post("/api/server_list/", target_data, content_type="application/json")
        self.assertEqual(r.status_code, 200)

        target_data = {
            "pk": target_pk,
            "name": "test sl 1",
            "readme": "test without server",
            "servers": [],
        }
        r = self.client.post("/api/server_list/", target_data, content_type="application/json")
        self.assertEqual(r.status_code, 200)
