import requests

from rev_manager.database import db_session
from rev_manager.models import TabUser, TabUserRoles
from rev_manager.services.user_auth import parse_token


class TestUserClass:
    url_login = "http://127.0.0.1:5000/api/login"
    url_user = "http://127.0.0.1:5000/api/user"
    def get_token(self):
        payload = {
            'email': 'jakub.urban@cezenergo.cz',
            'password': 'Energo2020'}
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", self.url_login, headers=headers, json=payload)
        data = response.json()
        return data['token']

    def test_login_as_admin(self):
        payload = {
            'email': 'jakub.urban@cezenergo.cz',
            'password': 'Energo2020'}
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", self.url_login, headers=headers, json=payload)
        assert response.status_code == 200

    def test_login_as_admin_bad_pass(self):
        payload = {
            'email': 'jakub.urban@cezenergo.cz',
            'password': 'Energo'}
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", self.url_login, headers=headers, json=payload)
        assert response.status_code == 401
        assert response.json() == {"message": "invalid username/password"}

    def test_add_user(self):
        payload = {
            "user": {
                "autor": 1,
                "email": "test.user@cezenergo.cz",
                "is_enabled": True,
                "name": "Test",
                "password": "Energo2020",
                "phone": "123456789",
                "surname": "User"
            },
            "roles": [
                1
            ]
        }
        headers = {
            'Authorization': 'Bearer ' + self.get_token(),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", self.url_user, headers=headers, json=payload)
        assert response.status_code == 200

    def test_user_is_exist(self):
        user = db_session.query(TabUser).filter(TabUser.email == "test.user@cezenergo.cz").one()
        assert user.email == "test.user@cezenergo.cz"
        assert user.name == "Test"
        assert user.surname == "User"

    def test_user_delete(self):
        # Find Association and delete
        user = db_session.query(TabUser).filter(TabUser.email == "test.user@cezenergo.cz").one()
        url = self.url_user + "/{0}".format(user.id)

        headers = {
            'Authorization': 'Bearer ' + self.get_token(),
        }

        response = requests.request("DELETE", url, headers=headers)
        assert response.status_code == 200

