# -*- coding: utf-8 -*-
import json

import flask_restful
from flask import jsonify, request, Response
from marshmallow import Schema, fields

from rev_manager.database import db_session
from rev_manager.models.models import TabRevisions, TabDevice, TabLocation, TabRevisionTypes
from rev_manager.schema import DevicesSchema, DevicesSchemaNested, LocationsSchemaNested, \
    UserSchema


class Device(flask_restful.Resource):
    def get(self, id):
        device = db_session.query(TabDevice)\
            .join(TabRevisions, TabDevice.revision)\
            .filter(TabDevice.id == id).first()
        schema = DevicesSchemaNested()
        result = schema.dump(device)
        response = jsonify(result)
        return response

    def put(self, id):
        device = db_session.query(TabDevice).filter(TabDevice.id == id).first()
        device.id_location = request.json['id_location']
        device.id_device_type = request.json['id_device_type']
        device.id_category = request.json['id_category']
        device.id_acc_center = request.json['id_acc_center']
        device.update()
        return Response(status=200)

    def delete(self, id):
        db_session.query(TabDevice).filter(TabDevice.id == id).delete()
        db_session.commit()
        return Response(status=200)


class Devices(flask_restful.Resource):
    def get(self):
        device = db_session.query(TabDevice).all()
        schema = DevicesSchema(many=True)
        result = schema.dump(device)
        response = jsonify(result)
        return response

    def post(self):
        try:
            # TODO: Upravit na lepší zápis pomocí Marshmallow loads
            allowed_revisions = request.json['allowed_rev_type']
            new_device = TabDevice(name=request.json['deviceName'],
                                   id_location=request.json['id_location'],
                                   id_device_type=request.json['id_device_type'],
                                   id_category=request.json['id_category'],
                                   id_acc_center=request.json['deviceIdAccCenter'],
                                   autor=1,
                                   description=request.json['deviceDescription'])

            # TODO: Upravi duplicity
            for item in allowed_revisions:
                allowed_revision = db_session.query(TabRevisionTypes).filter(TabRevisionTypes.id == item).first()
                new_device.allowed_rev_type.append(allowed_revision)

            TabDevice.add(new_device)
            return Response(status=201)
        except TypeError as error:
            print(error)
            return Response(status=400)

class DevicesSelect(flask_restful.Resource):
    def get(self):
        device = db_session.query(TabDevice).all()
        schema = DevicesSchema(many=True, only=("id", "name", "id_device_type"))
        result = schema.dump(device)
        response = jsonify(result)
        return response


# //TODO: Upravit na novu verzi
class Location(flask_restful.Resource):
    def get(self, id):
        location = db_session.query(TabLocation).filter(TabLocation.id == id).first()
        schema = LocationSchemaLoc()
        result = schema.dump(location)
        response = jsonify(result)
        return response


    def put(self, id):
        location = db_session.query(TabLocation).filter(TabLocation.id == id).first()
        location.name = request.json['name'],
        location.id_lic=request.json['id_lic'],
        location.id_acc_center=request.json['id_acc_center'],
        location.autor=1
        location.update()
        return Response(status=200)

    def delete(self, id):
        db_session.query(TabLocation).filter(TabLocation.id == id).delete()
        db_session.commit()
        return Response(status=200)

class RevisionTypeSchemaLoc(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()
    expiration = fields.Int()
    exp_reminder = fields.Int()


class RevisionSchemaLoc(Schema):
    id = fields.Int()
    name = fields.Str()
    revision_id = fields.Str()
    realization = fields.DateTime()
    authorize = fields.Bool()
    id_group = fields.Int()
    is_fault = fields.Bool()
    rev_v = fields.Bool()
    rev_p = fields.Bool()
    rm_authorization = fields.Bool()
    rm_authorized = fields.Bool()
    revision_type = fields.Nested(RevisionTypeSchemaLoc())
    technician = fields.Nested(UserSchema())

class AllRevisionTypeSchemaLoc(Schema):
    id = fields.Int()
    name = fields.String()
    description = fields.String()

class DeviceSchemaLoc(Schema):
    id = fields.Int()
    name = fields.Str()
    id_category = fields.Int()
    allowed_rev_type = fields.Nested(AllRevisionTypeSchemaLoc(many=True))
    revision = fields.Nested(RevisionSchemaLoc(many=True))

class LocationSchemaLoc(Schema):
    id = fields.Int()
    name = fields.Str()
    id_acc_center = fields.Str()
    devices = fields.Nested(DeviceSchemaLoc(many=True))
    owner = fields.Nested(UserSchema(many=True))


class Locations(flask_restful.Resource):
    def get(self):
        locations = db_session.query(TabLocation).all()
        schema = LocationsSchemaNested(many=True)
        result = schema.dump(locations)
        response = jsonify(result)
        db_session.close()
        return response

    def post(self):
        try:
            new_loc = TabLocation(name=request.json['name'],
                                  id_lic=0,
                                  id_acc_center=request.json['id_acc_center'],
                                  autor=1)
            TabLocation.add(new_loc)
            return Response(status=201)
        except TypeError as error:
            print(error)
            return Response(status=400)

class LocationsSelect(flask_restful.Resource):
    def get(self):
        device = db_session.query(TabLocation).all()
        schema = DevicesSchema(many=True, only=("id", "name"))
        result = schema.dump(device)
        response = jsonify(result)
        return response