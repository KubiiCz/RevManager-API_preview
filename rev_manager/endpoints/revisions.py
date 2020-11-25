# -*- coding: utf-8 -*-
import json
import os
from pprint import pprint

import flask_restful
from flask import jsonify, Response, request, send_file
from rev_manager import cli
from marshmallow import Schema, fields
from sqlalchemy import and_, func

from rev_manager.database import db_session
from rev_manager.models.models import TabRevisions, TabDevice, TabRevisionTypes, TabUser, Pricelist, TabLocation
from rev_manager.schema.schemas import DevicesSchemaNested, UserSchema, RevisionTypesSchemaNested, LocationsSchemaNested

# // - TODO: Možné použít tabulku licencí.
from rev_manager.services.fileHandler import RevFile, translate_rev_name


# Resouce for endpoint /revision
from rev_manager.services.user_auth import user_from_request


class Revision(flask_restful.Resource):
    # REST - GET Revision {id}
    def get(self, id):
        revision = db_session.query(TabRevisions, TabDevice, TabRevisionTypes, TabUser, Pricelist) \
            .join(TabDevice, TabRevisions.id_device == TabDevice.id) \
            .join(TabRevisionTypes, TabRevisions.id_rev == TabRevisionTypes.id) \
            .join(TabUser, TabRevisions.id_technician == TabUser.id) \
            .join(Pricelist,
                  and_(TabRevisions.id_rev == Pricelist.id_rev_type, TabDevice.id_category == Pricelist.id_cat)) \
            .filter(TabRevisions.id == id).first()
        schema = RevissionsSchemaEnd(many=True)
        result = schema.dump(revision)
        response = jsonify(result)
        return Response(response=jsonify(response), status=200, )

    # REST - PUT Revision {id}
    def put(self, id):
        device = db_session.query(TabRevisions).filter(TabRevisions.id == id).first()
        device.id_location = request.json['id_location']
        device.id_device_type = request.json['id_device_type']
        device.id_category = request.json['id_category']
        device.id_acc_center = request.json['id_acc_center']
        device.update()
        return Response(status=200)

    # REST - DELETE Revision {id}
    def delete(self, id):
        db_session.query(TabRevisions).filter(TabRevisions.id == id).delete()
        db_session.commit()
        return Response(status=200)


class RevissionDeviceSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    id_location = fields.Int()
    id_category = fields.Int()
    id_acc_center = fields.Str()
    location = fields.Pluck(LocationsSchemaNested, 'id_acc_center')


# Scheme for cls Revission - GET
class RevissionsSchemaEnd(Schema):
    id = fields.Int()
    surname = fields.Str()
    realization = fields.DateTime()
    expiration = fields.Int()
    fix_date = fields.DateTime()
    authorize = fields.Bool()
    id_technician = fields.Int()
    id_rev = fields.Int()
    device = fields.Nested(RevissionDeviceSchema())
    technician = fields.Nested(UserSchema())
    is_fault = fields.Bool()
    rm_authorization = fields.Bool()
    price = fields.Int()
    revision_type = fields.Nested(RevisionTypesSchemaNested())
    rev_v = fields.Bool()
    rev_p = fields.Bool()
    rev_z = fields.Bool()


class Revisions(flask_restful.Resource):
    def get(self):
        revision = db_session.query(TabRevisions) \
            .join(TabDevice, TabRevisions.device) \
            .join(TabRevisionTypes, TabRevisions.revision_type) \
            .join(TabUser, TabRevisions.technician) \
            .all()
        rev_result = RevissionsSchemaEnd(many=True).dump(revision)
        response = jsonify(rev_result)
        print(response.json)
        db_session.close()
        return response

    # TODO: Dodělat ukládání file
    def post(self):
        # try:
        data = json.loads(request.form['data'])
        print(data)

        """
        Class for save file
        f = File() # Class init

        - file from request
        - filename: Custom or name of file
        - data from json for make PATH

        PATH build style:
        id_location/id_device/id_revisionTypesGroup/id_revision
        """

        # Find device for recognize ACC Centre
        device = db_session.query(TabDevice) \
            .join(TabLocation, TabDevice.location) \
            .filter(TabDevice.id == data['id_device']).first()

        # Find last ID in revission for filename
        last_id = db_session.query(func.max(TabRevisions.id)).scalar()
        if last_id is None:
            last_id = 0

        f = RevFile()
        f.setRelativePath(loc_acc=device.location.id_acc_center,
                          device_acc=device.id_acc_center)
        f.filename = str(last_id + 1)

        # File saving Logic
        if data['file_v'] is not None:
            rev_v = request.files['file_v']
            f.saveFile(file=rev_v, file_type="def")

        if data['file_p'] is not None:
            rev_p = request.files['file_p']
            f.saveFile(file=rev_p, file_type="period")

        if data['file_z'] is not None:
            rev_z = request.files['file_z']
            f.saveFile(file=rev_z, file_type="bug")

        try:
            fix_date = data['fix_date']
        except BaseException as exc:
            print(exc)
            fix_date = None

        # Add to database
        new_revission = TabRevisions(realization=data['realization'],
                                     authorize=False,
                                     id_device=data['id_device'],
                                     id_technician=user_from_request(request),
                                     id_rev=data['id_revisionType'],
                                     is_fault=data['is_fault'],
                                     rm_authorization=data['rm_authorization_required'],
                                     autor=user_from_request(request),
                                     rev_v=True if data['file_v'] is not None else False,
                                     rev_p=True if data['file_p'] is not None else False,
                                     rev_z=True if data['file_z'] is not None else False,
                                     fix_date=fix_date,
                                     expiration=data['expiration'])
        TabRevisions.add(new_revission)

        return Response(status=201)

        # except BaseException as error:
        #     print(error)
        #     return Response(status=400)


class RevisionFile(flask_restful.Resource):
    def get(self, id, attachment_type):
        obj_revisson = db_session.query(TabRevisions)\
            .join(TabDevice, TabRevisions.device)\
            .join(TabLocation, TabDevice.location) \
            .join(TabRevisionTypes, TabRevisions.revision_type)\
            .filter(TabRevisions.id == id).first()

        # Filename for export
        attachment_filename = translate_rev_name(obj_revisson.device.location.name) \
                              + "-" + translate_rev_name(obj_revisson.revision_type.name) \
                              + "-" + attachment_type + ".pdf"

        path = "D:/RevManager/UPLOAD_FILES/{0}/{1}/{2}.pdf".format(
            obj_revisson.device.location.id_acc_center,
            obj_revisson.device.id_acc_center,
            str(obj_revisson.id) + "-" + attachment_type)
        return send_file(path, as_attachment=True, attachment_filename=attachment_filename)

    def post(self):
        data = json.loads(request.form['data'])
        id_revision = data['id']
        attachment_type = data['type']

        obj_revisson = db_session.query(TabRevisions) \
            .join(TabDevice, TabRevisions.device) \
            .join(TabLocation, TabDevice.location) \
            .join(TabRevisionTypes, TabRevisions.revision_type) \
            .filter(TabRevisions.id == id_revision).first()

        f = RevFile()
        f.setRelativePath(loc_acc=obj_revisson.device.location.id_acc_center,
                          device_acc=obj_revisson.device.id_acc_center)
        f.filename = str(id_revision)

        # File saving Logic
        if attachment_type == 'def':
            rev_v = request.files['file']
            f.saveFile(file=rev_v, file_type="def")
            obj_revisson.rev_v = True
            obj_revisson.update()

        elif attachment_type == 'periodic':
            rev_p = request.files['file']
            f.saveFile(file=rev_p, file_type="period")
            obj_revisson.rev_p = True
            obj_revisson.update()

        elif attachment_type == 'bug':
            rev_z = request.files['file']
            f.saveFile(file=rev_z, file_type="bug")
            obj_revisson.rev_z = True
            obj_revisson.fix_date = data['fix_date']
            obj_revisson.update()
        else:
            pass
        return "", 200
