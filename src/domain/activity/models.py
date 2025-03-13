from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    track = Column(String)
    long_name = Column(String)
    additional_data = Column(String)
    auto_release_month_and_day = Column(String)
    complete_winthin_days = Column(String)
    grades = Column(String)  
    sequence_number = Column(Integer)
    reward_points = Column(Integer)
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

