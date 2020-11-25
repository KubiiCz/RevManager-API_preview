from marshmallow import fields, Schema, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from rev_manager.models.models import TabGroupOfRevTypes, TabRevisionTypes, TabGroupRevJoin, TabDevice, TabLocation, \
    TabUser, TabRevisions, TabRole


class RolesSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    phone = fields.Str()
    name = fields.Str()
    surname = fields.Str()
    password = fields.Str()
    is_enabled = fields.Bool()
    autor = fields.Int()
    lastlogin = fields.DateTime()
    roles = fields.Nested(RolesSchema, many=True)
    owned_loc = fields.Nested(lambda: LocationsSchemaNested(only=('id', 'name'), many=True))

class UserSchemaPut(Schema):
    email = fields.Email(required=True)
    phone = fields.Str(required=False)
    name = fields.Str(required=False)
    surname = fields.Str(required=False)
    password = fields.Str(required=True)
    is_enabled = fields.Bool(default=True)
    autor = fields.Int(default=None)
    roles = fields.Pluck(RolesSchema, 'id', many=True, required=False)


    @post_load
    def make_user(self, data, **kwargs):
        return TabUser(**data)

class RevissionsSchema(Schema):
    price = fields.Int()


class RevissionsSchemaNested(Schema):
    id = fields.Int()
    realization = fields.DateTime()
    authorize = fields.Bool()
    id_device = fields.Int()
    id_group = fields.Int()
    id_technician = fields.Int()
    id_rev = fields.Int()
    is_fault = fields.Bool()
    rm_authorization = fields.Bool()
    # revision_type = fields.Nested(RevisionTypesSchemaNested())

"""
Group of Revision Types
Revision Types
"""
# Schema for JSON serialize data from model : Simple query with children
class RevisionTypesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TabRevisionTypes
        include_relationships = True
        load_instance = True

# Schema for JSON serialize data from model : Simple query without children
class RevisionTypesSchemaNested(Schema):
    id = fields.Int()
    created_time = fields.DateTime()
    updated_time = fields.DateTime()
    autor = fields.Int()
    name = fields.String()
    description = fields.String()
    expiration = fields.Int()
    exp_reminder = fields.Int()
    revision = fields.Nested(RevissionsSchemaNested(many=True))
    group = fields.Nested(lambda: GroupOfRevTypesSchemaNested(many=True, only=("id", "name")))

# Schema for JSON serialize data from model : Simple query without children
class GroupOfRevTypesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TabGroupOfRevTypes
        include_relationships = True
        load_instance = True


# Schema for JSON serialize data from model : Simple query with children
class GroupOfRevTypesSchemaNested(Schema):
    id = fields.Int()
    created_time = fields.DateTime()
    updated_time = fields.DateTime()
    autor = fields.Int()
    name = fields.String()
    description = fields.String()
    rev_type = fields.Nested(RevisionTypesSchemaNested(many=True, exclude=("group",)))


class GroupOfRevTypesSchemaSel(Schema):
    id = fields.Int()
    name = fields.String()
    rev_type = fields.Nested(RevisionTypesSchemaNested(many=True, only=("id", "name")))

# Join table
class TabGroupRevJoinSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TabGroupRevJoin
        include_relationships = True
        load_instance = True


"""
Devices and Locations
"""
class DevicesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TabDevice
        include_relationships = True
        load_instance = True



class DevicesSchemaNested(Schema):
    id = fields.Int()
    name = fields.Str()
    created_time = fields.DateTime()
    updated_time = fields.DateTime()
    autor = fields.Int()
    id_location = fields.Int()
    id_category = fields.Int()
    id_acc_center = fields.Str()
    allowed_rev_type = fields.Nested(RevisionTypesSchemaNested(many=True))
    revision = fields.Nested(RevissionsSchemaNested(many=True))



class LocationsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TabLocation
        include_relationships = True
        load_instance = True

class LocationsSchemaNested(Schema):
    id = fields.Int()
    created_time = fields.DateTime()
    updated_time = fields.DateTime()
    autor = fields.Int()
    name = fields.Str()
    id_lic = fields.Int()
    id_acc_center = fields.Str()
    devices = fields.Nested(DevicesSchemaNested(many=True))
    owner = fields.Nested(UserSchema(exclude=("owned_loc",), many=True))