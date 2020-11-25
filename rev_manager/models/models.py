# -*- coding: utf-8 -*-
import time

from sqlalchemy import Column, Integer, String, BIGINT, LargeBinary, Boolean, ForeignKey, DateTime, func, text
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.ext.declarative.base import declared_attr
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash

from rev_manager.database import Base, db_session


def session_commit():
    try:
        db_session.commit()
    except BaseException as exc:
        print(str(exc))
    finally:
        db_session.close()


# BASE
class TableBase(object):
    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_time = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_time = Column(TIMESTAMP, nullable=False,
                          server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    autor = Column(Integer, unique=False, nullable=True)

    def __init__(self, autor=None):
        self.autor = autor

    def __repr__(self):
        return str(self.__dict__)

    def dict(self):
        return self.__dict__

    # Add method
    @staticmethod
    def add(data):
        db_session.add(data)
        session_commit()
        return

    # Update data method
    def update(self):
        session_commit()
        return

    # Delete method
    @staticmethod
    def delete(self):
        db_session.delete(self)
        session_commit()
        return


# ---

# Revisions
# TODO: Styling
class TabRevisions(TableBase, Base):
    __tablename__ = 'revisions'
    realization = Column(DateTime, unique=False, nullable=False)  # Date
    rev_v = Column(Boolean, default=0, unique=False, nullable=True)
    rev_p = Column(Boolean, default=0, unique=False, nullable=True)
    rev_z = Column(Boolean, default=0, unique=False, nullable=True)
    authorize = Column(Boolean, default=0)
    id_device = Column(Integer(), ForeignKey('devices.id'))
    id_technician = Column(Integer(), ForeignKey('users.id'))
    id_rev = Column(Integer(), ForeignKey('revision_types.id'))
    is_fault = Column(Boolean, default=0)
    fix_date = Column(DateTime, unique=False, nullable=True)
    rm_authorization = Column(Boolean, default=0)
    rm_authorized = Column(Boolean, default=0)
    device = relationship("TabDevice", backref="device")
    technician = relationship("TabUser", backref="technician")
    revision_type = relationship("TabRevisionTypes", backref="revision_type")
    expiration = Column(Integer, unique=False, nullable=True)

    def __init__(self, autor, realization, rev_v, rev_p, rev_z, authorize, id_device, id_technician, id_rev, is_fault,
                 fix_date,
                 rm_authorization,
                 expiration ):
        super().__init__(autor)
        self.expiration = expiration
        self.fix_date = fix_date
        self.rev_v = rev_v
        self.rev_p = rev_p
        self.rev_z = rev_z
        self.realization = realization
        self.authorize = authorize
        self.id_device = id_device
        self.id_technician = id_technician
        self.id_rev = id_rev
        self.is_fault = is_fault
        self.rm_authorization = rm_authorization

    def getFile(self):
        return


# DEVICES
# Revisison Locations
# // - TODO: Možné použít tabulku licencí.
class TabLocation(TableBase, Base):
    __tablename__ = 'revision_locations'
    name = Column(String(256), unique=False, nullable=True)
    description = Column(String(256), unique=False, nullable=True)
    id_lic = Column(Integer)
    owner = relationship("TabUser", secondary="connector_locations_users", back_populates="owned_loc")
    devices = relationship("TabDevice", back_populates='location')
    id_acc_center = Column(String(50), unique=False)  # středisko první část

    def __init__(self, name, id_lic, id_acc_center, autor):
        super().__init__(autor)
        self.name = name
        self.id_lic = id_lic
        self.id_acc_center = id_acc_center


class TabLocOwners(TableBase, Base):
    __tablename__ = 'connector_locations_users'
    id_user = Column(Integer(), ForeignKey('users.id'))
    id_locaton = Column(Integer(), ForeignKey('revision_locations.id'))


# Devices
class TabDevice(TableBase, Base):
    __tablename__ = 'devices'
    name = Column(String(256), unique=False, nullable=True)
    description = Column(String(256), unique=False, nullable=True)
    id_device_type = Column(Integer, unique=False, nullable=True)  # DK, BK, KJ
    id_category = Column(Integer, unique=False, nullable=True)  # kat.
    id_acc_center = Column(String(50), unique=False)  # středisko druhá část
    allowed_rev_type = relationship("TabRevisionTypes", secondary="connector_device_rev_type",
                                    backref="parent1")  # připojené typy revizí
    revision = relationship('TabRevisions', backref='revision')
    id_location = Column(Integer, ForeignKey('revision_locations.id'))
    location = relationship('TabLocation', back_populates='devices')

    def __init__(self, name, id_location, id_device_type, id_category, id_acc_center, autor, description):
        super().__init__(autor)
        self.description = description
        self.name = name
        self.id_location = id_location
        self.id_device_type = id_device_type
        self.id_category = id_category
        self.id_acc_center = id_acc_center


class TabDeviceRevJoin(TableBase, Base):
    __tablename__ = 'connector_device_rev_type'
    id_device = Column(Integer(), ForeignKey('devices.id'))
    id_rev_type = Column(Integer(), ForeignKey('revision_types.id'))


# ---

# REVISION TYPES
# Group rev_types and Revision types connector table
class TabGroupRevJoin(TableBase, Base):
    __tablename__ = 'connector_rev_group_type'
    id_rev_group = Column(Integer(), ForeignKey('group_of_rev_types.id', ondelete="CASCADE"))
    id_rev_type = Column(Integer(), ForeignKey('revision_types.id', ondelete="CASCADE"))


# Group revtypes
class TabGroupOfRevTypes(TableBase, Base):
    __tablename__ = 'group_of_rev_types'
    name = Column(String(256), unique=False, nullable=True)
    description = Column(String(256), unique=False, nullable=True)
    rev_type = relationship("TabRevisionTypes",secondary="connector_rev_group_type", backref="parent",
                            cascade="all, delete")

    def __init__(self, name, description, autor):
        super().__init__(autor)
        self.name = name
        self.description = description


# Revision types
class TabRevisionTypes(TableBase, Base):
    __tablename__ = 'revision_types'
    name = Column(String(256), unique=False, nullable=True)
    description = Column(String(256), unique=False, nullable=True)
    expiration = Column(Integer, unique=False, nullable=True) # Měsíce (default value)
    exp_reminder = Column(Integer,unique=False, nullable=True)
    group = relationship("TabGroupOfRevTypes",secondary="connector_rev_group_type", 
    backref="children",passive_deletes=True)
    device = relationship("TabDevice",secondary="connector_device_rev_type", backref="childr")
    revisions = relationship('TabRevisions')

    def __init__(self, name, description, expiration, exp_reminder, autor):
        super().__init__(autor)
        self.exp_reminder = exp_reminder
        self.expiration = expiration
        self.description = description
        self.name = name


# OTHER
# Price List for Each technician
class Pricelist(TableBase, Base):
    __tablename__ = 'pricelist'
    id_rev_type = Column(Integer, unique=False, nullable=True)
    id_grou_rev = Column(Integer, unique=False, nullable=True)
    id_device = Column(Integer, unique=False, nullable=True)
    id_cat = Column(Integer, unique=False, nullable=True)
    price = Column(Integer)

    def __init__(self, id_rev_type, price, autor):
        super().__init__(autor)
        self.price = price
        self.id_rev_type = id_rev_type


# Enabling revisison reminder
class TabExpReminder(TableBase, Base):
    __tablename__ = 'exp_reminder'
    id_user = Column(Integer)
    remind = Column(Boolean, default=0)

    def __init__(self, id_user, remind, autor):
        super().__init__(autor)
        self.remind = remind
        self.id_user = id_user


# Device category
# Device type
# ---


# USERS
# Define Roles
class TabRole(TableBase, Base):
    __tablename__ = 'role'
    name = Column(String(50), unique=True)
    user = relationship("TabUser", secondary="user_roles")

    def __init__(self, name, autor):
        super().__init__(autor)
        self.name = name

    def list(self):
        return {'id': self.id, 'nazev': self.name}


# Define the UserRoles data model
class TabUserRoles(TableBase, Base):
    __tablename__ = 'user_roles'
    user_id = Column(Integer(), ForeignKey('users.id', ondelete="CASCADE"))
    role_id = Column(Integer(), ForeignKey('role.id', ondelete="CASCADE"))

    def __init__(self, user_id, role_id, autor):
        super().__init__(autor)
        self.user_id = user_id
        self.role_id = role_id


# Define User model
class TabUser(TableBase, Base):
    __tablename__ = 'users'
    email = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    name = Column(String(128), nullable=False)
    surname = Column(String(128), nullable=False)
    phone = Column(String(128), unique=False, nullable=True)
    is_enabled = Column(Boolean(), nullable=True, default=True)
    roles = relationship('TabRole', secondary="user_roles", back_populates="user", cascade="all, delete")
    owned_loc = relationship("TabLocation", secondary="connector_locations_users", back_populates="owner")
    lastlogin = Column(DateTime, nullable=True)

    def __init__(self, email, name, password, surname, phone=None, autor=None, is_enabled=True):
        super().__init__(autor)
        self.phone = phone
        self.surname = surname
        self.email = email
        self.name = name
        self.password = generate_password_hash(password)
        self.is_enabled = is_enabled

    def get_roles(self):
        roles_field = []
        if len(self.roles) > 1:
            for item in self.roles:
                roles_field.append(item.name)
            return roles_field
        else:
            return self.roles[0].name


