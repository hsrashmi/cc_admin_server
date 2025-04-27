from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, text, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from ...database import Base
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class ILPUser(Base):
    __tablename__ = "ilp_users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    profile_pic_url = Column(String, default=None)
    phone1 = Column(String, nullable=False)
    phone2 = Column(String, default=None)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    gender = Column(SqlEnum(GenderEnum), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"), nullable=False)
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships to track creator and updater
    creator = relationship("ILPUser", remote_side=[id], foreign_keys=[created_by])
    updater = relationship("ILPUser", remote_side=[id], foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
