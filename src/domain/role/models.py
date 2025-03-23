from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SqlEnum, text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ...database import Base

# Enums for structured constraints
class AccessTypeEnum(str, Enum):
    READ = "read"
    WRITE = "write"

class LevelEnum(str, Enum):
    ROOT = "root"
    STATE = "state"
    ZONE = "zone"
    DISTRICT = "district"
    BLOCK = "block"
    SCHOOL = "school"
    CLASS = "class"

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)  # Unique constraint added
    description = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}


class UserRole(Base):
    __tablename__ = "user_role_assignments"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("ilp_users.id"), nullable=False)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)

    access_type = Column(SqlEnum(AccessTypeEnum), nullable=False, default=AccessTypeEnum.WRITE)
    level = Column(SqlEnum(LevelEnum), nullable=False)
    level_id = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships
    user = relationship("ILPUser", foreign_keys=[user_id])
    role = relationship("Role", foreign_keys=[role_id])
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
