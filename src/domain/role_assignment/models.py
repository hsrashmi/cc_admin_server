from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SqlEnum, text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ...database import Base
from ..role.models import Role
from ..school.models import Class
from ..ilpuser.models import ILPUser

# Enums for structured constraints
class AccessTypeEnum(str, Enum):
    READ = "READ"
    WRITE = "WRITE"

class LevelEnum(str, Enum):
    ROOT = "ROOT"
    STATE = "STATE"
    ZONE = "ZONE"
    DISTRICT = "DISTRICT"
    BLOCK = "BLOCK"
    SCHOOL = "SCHOOL"
    CLASS = "CLASS"

class UserRole(Base):
    __tablename__ = "user_role_assignments"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("ilp_users.id"), nullable=False)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)

    access_type = Column(SqlEnum(AccessTypeEnum), nullable=False, default=AccessTypeEnum.WRITE)
    level = Column(SqlEnum(LevelEnum, name="levelenum"), nullable=False)
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
    
    # Define relationships for different levels
    class_info = relationship(
        "Class",
        foreign_keys=[level_id],
        primaryjoin="and_(UserRole.level_id == Class.id, UserRole.level == 'CLASS')",
        lazy="joined",
    )

    school_info = relationship(
        "School",
        foreign_keys=[level_id],
        primaryjoin="and_(UserRole.level_id == School.id, UserRole.level == 'SCHOOL')",
        lazy="joined",
    )

    block_info = relationship(
        "Block",
        foreign_keys=[level_id],
        primaryjoin="and_(UserRole.level_id == Block.id, UserRole.level == 'BLOCK')",
        lazy="joined",
    )

    district_info = relationship(
        "District",
        foreign_keys=[level_id],
        primaryjoin="and_(UserRole.level_id == District.id, UserRole.level == 'DISTRICT')",
        lazy="joined",
    )

    zone_info = relationship(
        "Zone",
        foreign_keys=[level_id],
        primaryjoin="and_(UserRole.level_id == Zone.id, UserRole.level == 'ZONE')",
        lazy="joined",
    )

    state_info = relationship(
        "State",
        foreign_keys=[level_id],
        primaryjoin="and_(UserRole.level_id == State.id, UserRole.level == 'STATE')",
        lazy="joined",
    )

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
