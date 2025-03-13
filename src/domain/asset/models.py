from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    description = Column(String)
    url = Column(String)
    size = Column(Integer)
    mime_type = Column(String)
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.id'))
    
    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}

