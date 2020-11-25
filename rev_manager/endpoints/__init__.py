from flask import Flask, Blueprint, Response
import flask_restful

from .devices import Device, Devices, Locations, Location, DevicesSelect, LocationsSelect
from .revision_groups import GroupsOfRevType, GroupOfRevType, RevisionType, RevisisonTypes, GroupsOfRevTypeSelect, \
    GroupOfRevTypeSelect, RevisisonTypesSelect
from .revisions import Revisions, Revision, RevisionFile
from .user_admin import User, Login, Role

api_hp_bp = Blueprint("main", __name__)
api_hp = flask_restful.Api(app=api_hp_bp)


# Main url:

# Locations
api_hp.add_resource(Locations, "/location")
api_hp.add_resource(LocationsSelect, "/location/select")
api_hp.add_resource(Location, "/location/<id>")

# Devices
api_hp.add_resource(Devices, "/device")
api_hp.add_resource(DevicesSelect, "/device/select")
api_hp.add_resource(Device, "/device/<id>")

# Revision Types
api_hp.add_resource(RevisisonTypes, "/revision_type")
api_hp.add_resource(RevisisonTypesSelect, "/revision_type/select")
api_hp.add_resource(RevisionType, "/revision_type/<id>")

# Revision Groups
api_hp.add_resource(GroupsOfRevType, "/group_rev_type")
api_hp.add_resource(GroupsOfRevTypeSelect, "/group_rev_type/select")
api_hp.add_resource(GroupOfRevType, "/group_rev_type/<id>")
api_hp.add_resource(GroupOfRevTypeSelect, "/group_rev_type/<id>/select")

# Revisions
api_hp.add_resource(Revisions, "/revision")
api_hp.add_resource(Revision, "/revision/<id>")
api_hp.add_resource(RevisionFile,"/revision/attachment/update" ,"/revision/attachment/<id>/<attachment_type>")

# User
api_hp.add_resource(User, "/user", "/user/<id>")
api_hp.add_resource(Role, "/role" , "/role/<id>")

# Login
api_hp.add_resource(Login, "/login")