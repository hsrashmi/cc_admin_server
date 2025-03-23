from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ...database import Base

# Define Enum for asset type
class AssetType(str, Enum):
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(SqlEnum(AssetType, name="asset_type_enum"), nullable=False)  # Restricted to valid values
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
