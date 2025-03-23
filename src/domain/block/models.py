from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from datetime import datetime
from ...database import Base
from ..district.models import District


class Block(Base):
    __tablename__ = "blocks"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    district_id = Column(String, ForeignKey("districts.id"), nullable=False)  # Enforce foreign key
    description = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships for easy querying
    district = relationship("District", backref="blocks")
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
