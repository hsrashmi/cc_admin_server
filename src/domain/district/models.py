from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from datetime import datetime
from ...database import Base
from ..zone.models import Zone


class District(Base):
    __tablename__ = "districts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)  # Enforce foreign key

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships for easy querying
    zone = relationship("Zone", backref="districts")
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
