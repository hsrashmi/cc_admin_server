from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base


class District(Base):
    __tablename__ = "districts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    zone_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.id'))
    
    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}

