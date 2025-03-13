from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, String, text, Enum as SqlEnum, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base
    
class School(Base):
    __tablename__ = "schools"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    long_name = Column(String)
    dise_code = Column(Integer)
    district_id = Column(String, ForeignKey('districts.id'))
    village_id = Column(String, ForeignKey('villages.id'))
    address = Column(String)
    city = Column(String)
    state = Column(String)
    pincode = Column(Integer)
    owner_id = Column(String, ForeignKey('ilp_users.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.id'))

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}


class Class(Base):
    __tablename__ = "classes"

    id = Column(String, primary_key=True)
    grade = Column(String, nullable=False)
    section = Column(String)
    school_id = Column(String, ForeignKey('schools.id'))
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.id'))

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}