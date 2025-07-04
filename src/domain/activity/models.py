from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
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
    complete_within_days = Column(Integer)  # Fixed data type
    grade = Column(String)  
    sequence_number = Column(Integer)
    reward_points = Column(Integer)
    description = Column(String)  

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    last_updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships with ILPUser
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])
    
    assets = relationship(
    "Asset",
    secondary="activity_assets",
    backref="activities"
)


    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
