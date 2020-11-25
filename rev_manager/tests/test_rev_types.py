# content of test_sample.py

import requests

from rev_manager.database import db_session
from rev_manager.models import TabRevisionTypes


class TestClass:
    def test_add_revision_type(self):
        json = {
            "expiration": 1,
            "exp_reminder": 15,
            "description": "test",
            "name": "Testovací revize",
            "autor": 1,
            "id_group": 1
        }
        response = requests.post("http://127.0.0.1:5000/api/revision_type", json=json)
        assert response.status_code == 201

    def test_get(self):
        rev_type = db_session.query(TabRevisionTypes).filter(TabRevisionTypes.name == "Testovací revize").one()
        assert rev_type.name == "Testovací revize"

    def test_delete(self):
        rev_type = db_session.query(TabRevisionTypes).filter(TabRevisionTypes.name == "Testovací revize").one()
        delete = requests.delete("http://127.0.0.1:5000/api/revision_type/{0}".format(rev_type.id))
        assert delete.status_code == 200



    # def test_get_revision_tybe_by_id(self):
    #     response = requests.get("http://127.0.0.1:5000/api/revision_type/1")
    #     data = response.json()
    #     json = {
    #         "autor": 1,
    #         "created_time": "2020-08-03T13:57:14",
    #         "description": "",
    #         "device": [],
    #         "exp_reminder": 14,
    #         "expiration": 12,
    #         "group": [1],
    #         "id": 1,
    #         "name": "ElektroTyp",
    #         "parent": [1],
    #         "parent1": [],
    #         "revision_type": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
    #         "revisions": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
    #         "updated_time": "2020-08-03T13:57:14"
    #     }
    #     assert response.status_code == 200
    #     assert data == json
