import time
from pprint import pprint

import flask_restful
from flask import jsonify, request, make_response
from werkzeug.security import check_password_hash

from rev_manager.database import db_session
from rev_manager.models import TabUser, TabRole, TabUserRoles, TabLocation, TabLocOwners
from rev_manager.schema import UserSchema, RolesSchema, UserSchemaPut
from rev_manager.services.user_auth import user_from_request, create_token, api_token_required


# JWT AUTh process end
class Login(flask_restful.Resource):
    def post(self):
        data = request.get_json(force=True)
        email = data['email']
        password = data['password']
        user = db_session.query(TabUser).filter(TabUser.email == email).first()

        if user == None:
            response = make_response(
                jsonify({"message": "invalid username/password"}))
            response.status_code = 401
            return response
        if check_password_hash(user.password, password):
            token = create_token(user)
            user.lastlogin = time.strftime('%Y-%m-%d %H:%M:%S')
            user.update()
            return {'token': token}, 200
        else:
            response = make_response(
                jsonify({"message": "invalid username/password"}))
            response.status_code = 401
            return response


class User(flask_restful.Resource):
    @api_token_required("admin")
    def get(self, id=None):
        if id:
            try:
                user = db_session.query(TabUser).filter(TabUser.id == id).one()
                user_schema = UserSchema().dump(user)
                db_session.close()
                return jsonify(user_schema)
            except BaseException as exc:
                return str(exc), 404
        else:
            users = db_session.query(TabUser).all()
            users_schema = UserSchema(many=True).dump(users)
            db_session.close()
            return jsonify(users_schema)


    def put(self, id):
        user = db_session.query(TabUser).filter(TabUser.id == id).one()
        user.autor = user_from_request(request)

        roles = request.json['roles']
        owned_loc = request.json['owned_loc']

        # User update
        user.email = request.json['email']
        user.name = request.json['name']
        user.surname = request.json['surname']
        user.phone = request.json['phone']
        user.is_enabled = request.json['is_enabled']

        # TODO: Rebuild to efficient variant
        # Deleting all roles from user Association table
        asso = db_session.query(TabUserRoles).filter(TabUserRoles.user_id == id).all()
        for item in asso:
            db_session.delete(item)
            print('Deleted', item.role_id)
        db_session.commit()

        # Appending roles to user
        for item in roles:
            role = db_session.query(TabRole).filter(TabRole.id == item['id']).first()
            user.roles.append(role)
            print('Appended', role.name)

        # Deleting owned locations from Association table
        owned_loc_asso = db_session.query(TabLocOwners).filter(TabLocOwners.id_user == id).all()
        for item in owned_loc_asso:
            db_session.delete(item)
        db_session.commit()

        #Appending onwed_loc to user
        for item in owned_loc:
            location = db_session.query(TabLocation).filter(TabLocation.id == item['id']).first()
            user.owned_loc.append(location)

        user.update()
        return

    @api_token_required("admin")
    def post(self):
        # TODO:Ošetřit duplicity
        """
        Example of User JSON for POST method:
        {
            "user": {
                "autor": 1,
                "email": "test.user3@cezenergo.cz",
                "is_enabled": true,
                "name": "Test",
                "password": "Energo2020",
                "phone": "123456789",
                "surname": "User 3"
            },
            "roles": [
                1,
                2
            ]
        }
        """
        # Get data from JSON
        global isAdded
        response = request.get_json()
        res_role = response['roles']
        res_user = response['user']

        # Deserialize JSON to Obj User over UserSchemaPut
        user = UserSchemaPut().load(res_user)
        user.autor = user_from_request(request)

        # Appending roles to User
        print(res_role)
        for item in res_role:
            role = db_session.query(TabRole).filter(TabRole.id == item).first()
            user.roles.append(role)

        # Add and commmt do DB
        user.add(user)
        return

    @api_token_required("admin")
    def delete(self, id):
        try:
            # Find Association and delete
            asso = db_session.query(TabUserRoles).filter(TabUserRoles.user_id == id).all()
            for item in asso:
                item.delete(item)

            # Delete User
            user = db_session.query(TabUser).filter(TabUser.id == id).one()
            user.delete(user)
            return "", 200

        except BaseException as exc:
            return str(exc), 404

class Role(flask_restful.Resource):
    def get(self, id=None):
        if id:
            try:
                role = db_session.query(TabRole).filter(TabRole.id == id).one()
                role_schema = RolesSchema().dump(role)
                db_session.close()
                return jsonify(role_schema)
            except BaseException as exc:
                return str(exc), 404

        else:
            role = db_session.query(TabRole).all()
            role_schema = RolesSchema(many=True).dump(role)
            db_session.close()
            return jsonify(role_schema)

    def put(self, id):
        return

    def post(self):
        return

    def delete(self, id):
        return
