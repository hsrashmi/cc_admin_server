from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ...database import Base

# Define Enum for asset type
class AssetTypeEnum(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(SqlEnum(AssetTypeEnum, name="assettypeenum"), nullable=False)  # Restricted to valid values
    description = Column(String)
    url = Column(String, unique=True, nullable=False)  # Enforcing uniqueness
    size = Column(Integer)
    mime_type = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships with ILPUser
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}

class ActivityAsset(Base):
    __tablename__ = "activity_assets"

    id = Column(String, primary_key=True)
    activity_id = Column(String, ForeignKey("activities.id"))
    asset_id = Column(String, ForeignKey("assets.id"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships with ILPUser
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    activity = relationship("Activity", foreign_keys=[activity_id])
    asset = relationship("Asset", foreign_keys=[asset_id])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}