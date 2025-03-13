from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base


class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    state_id = Column(String)
    description = Column(String)
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.id'))
    
    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}

