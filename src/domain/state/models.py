from sqlalchemy import Column, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from datetime import datetime
from ...database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)  # Changed from `long_name` to `name` with uniqueness
    description = Column(String)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships for easier querying
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
