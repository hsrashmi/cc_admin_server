from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SqlEnum, text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ...database import Base

class RoleEnum(str, Enum):
    ROOT = "ROOT"
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    BLOCK_MANAGER = "BLOCK_MANAGER"
    DISTRICT_MANAGER = "DISTRICT_MANAGER"
    ZONE_MANAGER = "ZONE_MANAGER"
    STATE_MANAGER = "STATE_MANAGER"

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True)
    name = Column(SqlEnum(RoleEnum, name="roleenum"), nullable=False, unique=True)  # Unique constraint added
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
