import time

from flask import  request,  jsonify, make_response

from werkzeug.security import generate_password_hash, check_password_hash
import flask_restful

import jwt
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from functools import wraps

from rev_manager.config import Config
from rev_manager.database import db_session
from rev_manager.models import TabUser


# Create token from user informations
def create_token(user):
    payload = {
        'sub': user.id,
        'email': user.email,
        'roles': user.get_roles(),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=120)
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    return token.decode('unicode_escape')

# Parsing user informations form Bearer: Token
def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, Config.SECRET_KEY, algorithms='HS256')

# Login decorator function
"""
api_token_required decorator for allow pass users with specific roles to endpoints
Example: @api_token_required("admin","location")
"""
def api_token_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.headers.get('Authorization'):
                response = jsonify(message='Missing authorization header')
                response.status_code = 403
                return response
            try:
                payload = parse_token(request)
            except DecodeError:
                response = jsonify(message='Token is invalid')
                response.status_code = 401
                return response
            except ExpiredSignature:
                response = jsonify(message='Token has expired')
                response.status_code = 401
                return response
            user_id = payload['sub']
            user = db_session.query(TabUser).filter_by(id=user_id).first()
            roles_list = user.get_roles()
            if not (roles[0] in roles_list or 'admin' in roles):
                response = jsonify(message='Unauthorized role')
                response.status_code = 403
                return response
            return f(*args, **kwargs)
        return decorated_function
    return wrapper


# TODO: Fix pass changing
class PassChange(flask_restful.Resource):
    @api_token_required()
    def put(self):
        user_id = parse_token(request)['sub']
        data = request.get_json(force=True)
        pheslo = data['pheslo']
        nheslo = data['nheslo']
        user = TabUser.query.filter_by(id=user_id).first()
        if user:
            if (check_password_hash(user.password, pheslo) or user.password == ''):
                user.password = generate_password_hash(nheslo)
                try:
                    db_session.commit()
                    response = make_response(jsonify({"message": "OK"}))
                    response.status_code = 200
                except:
                    response = make_response(jsonify({"message": "ERROR"}))
                    response.status_code = 500
                return response
            else:
                response = make_response(jsonify({"message": "ivalid password"}))
                response.status_code = 401
                return response
        else:
            response = make_response(jsonify({"message": "invalid user"}))
            response.status_code = 401
            return  response

# Func for parse user from Token
def user_from_request(request):
    payload = parse_token(request)
    user_id = payload['sub']
    return user_id