from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base


class Organization(Base):
    __tablename__ = "organizations"

    organization_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    long_name = Column(String)
    description = Column(String)
    placeholder1 = Column(String)
    placeholder2 = Column(String)
    placeholder3 = Column(String)  
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, ForeignKey('ilp_users.user_id'))
    last_updated_by =  Column(String, ForeignKey('ilp_users.user_id'))
    
    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}

