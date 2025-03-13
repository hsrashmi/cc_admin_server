from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, String, text, Enum as SqlEnum, ForeignKey, inspect
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base
    
class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True)    
    name = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, nullable=False)
    last_updated_by =  Column(String, default=None)

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}


class UserRole(Base):
    __tablename__ = "user_role_assignments"

    id = Column(String, primary_key=True)    
    user_id = Column(String, ForeignKey('ilp_users.id'), nullable=False)
    role_id = Column(String, ForeignKey('roles.id'), nullable=False)
    access_type = Column(String, nullable=False, default='write')
    level = Column(String, nullable=False)
    level_id = Column(String)  
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.id'))

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}