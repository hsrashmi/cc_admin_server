from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, String, text, Enum as SqlEnum, ForeignKey, inspect
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from ...database import Base
    
class ILPUser(Base):
    __tablename__ = "ilp_users"

    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    profile_pic_url = Column(String, default=None)
    phone1 = Column(String)
    phone2 = Column(String, default=None)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    gender = Column(String)
    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), default=None)
    created_by = Column(String, nullable=False)
    last_updated_by =  Column(String, default=None)

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
