from pprint import pprint

import flask_restful
from flask import request, jsonify, Response

from rev_manager.database import db_session
from rev_manager.models.models import TabGroupOfRevTypes, TabRevisionTypes, TabGroupRevJoin
from rev_manager.schema.schemas import GroupOfRevTypesSchemaNested, RevisionTypesSchemaNested, \
    RevisionTypesSchema, GroupOfRevTypesSchemaSel

"""
Read/Edit/Delete RevisionGroup selected by ID
"""


class GroupOfRevType(flask_restful.Resource):
    def get(self, id):
        rev_group = db_session.query(TabGroupOfRevTypes).filter(TabGroupOfRevTypes.id == id).first()
        schema = GroupOfRevTypesSchemaNested()
        result = schema.dump(rev_group)
        response = jsonify(result)
        return response

    def put(self, id):
        rev_group = db_session.query(TabGroupOfRevTypes).filter(TabGroupOfRevTypes.id == id).first()
        rev_group.name = request.json['name']
        rev_group.description = request.json['description']
        rev_group.update()
        return Response(status=200)

    def delete(self, id):
        db_session.query(TabGroupOfRevTypes).filter(TabGroupOfRevTypes.id == id).delete()
        db_session.commit()
        return Response(status=200)


"""
Read all RevisionTypes or create new RevisionType
"""


class GroupsOfRevType(flask_restful.Resource):
    def get(self):
        rev_type = db_session.query(TabGroupOfRevTypes).all()
        schema = GroupOfRevTypesSchemaNested(many=True)
        result = schema.dump(rev_type)
        response = jsonify(result)
        return response

    def post(self):
        new_rev_type = TabGroupOfRevTypes(name=request.json['name'],
                                          description=request.json['description'],
                                          autor=1)
        TabGroupOfRevTypes.add(new_rev_type)
        return


"""
Read/Edit/Delete RevisionType selected by ID
"""


class RevisionType(flask_restful.Resource):
    def get(self, id):
        rev_type = db_session.query(TabRevisionTypes).filter(TabRevisionTypes.id == id).first()
        schema = RevisionTypesSchema()
        result = schema.dump(rev_type)
        response = jsonify(result)
        return response

    def put(self, id):
        rev_type = db_session.query(TabRevisionTypes).filter(TabRevisionTypes.id == id).first()
        rev_type.name = request.json['name']
        rev_type.description = request.json['description']
        rev_type.expiration = request.json['expiration']
        rev_type.exp_reminder = request.json['exp_reminder']
        rev_type.update()
        return Response(status=200)

    def delete(self, id):
        db_session.query(TabGroupRevJoin).filter(TabGroupRevJoin.id_rev_type == id).delete()
        db_session.query(TabRevisionTypes).filter(TabRevisionTypes.id == id).delete()
        db_session.commit()
        return "", 200


"""
Read all RevisionTypes or create new RevisionType
"""


class RevisisonTypes(flask_restful.Resource):
    def get(self):
        rev_type = db_session.query(TabRevisionTypes).all()
        schema = RevisionTypesSchemaNested(many=True)
        result = schema.dump(rev_type)
        response = jsonify(result)
        return response

    def post(self):
        try:
            new_rev_type = TabRevisionTypes(name=request.json['name'],
                                            description=request.json['description'],
                                            expiration=request.json['expiration'],
                                            exp_reminder=request.json['exp_reminder'],
                                            autor=1)
            group = db_session.query(TabGroupOfRevTypes).filter(TabGroupOfRevTypes.id == request.json['id_group']).first()
            new_rev_type.group.append(group)

            print(new_rev_type)
            TabRevisionTypes.add(new_rev_type)
            return "", 201
        except BaseException as e:
            print(e)
            return flask_restful.abort(409)


"""
Selects for ALL
"""

class GroupsOfRevTypeSelect(flask_restful.Resource):
    def get(self):
        rev_type = db_session.query(TabGroupOfRevTypes).all()
        schema = GroupOfRevTypesSchemaNested(many=True, only=("id", "name"))
        result = schema.dump(rev_type)
        response = jsonify(result)
        return response

class GroupOfRevTypeSelect(flask_restful.Resource):
    def get(self, id):
        rev_group = db_session.query(TabGroupOfRevTypes).filter(TabGroupOfRevTypes.id == id).first()
        schema = GroupOfRevTypesSchemaSel()
        result = schema.dump(rev_group)
        response = jsonify(result)
        return response

class RevisisonTypesSelect(flask_restful.Resource):
    def get(self):
        rev_type = db_session.query(TabRevisionTypes).all()
        schema = RevisionTypesSchemaNested(many=True, only=("id", "name"))
        result = schema.dump(rev_type)
        response = jsonify(result)
        return response