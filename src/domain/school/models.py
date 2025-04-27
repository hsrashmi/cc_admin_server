from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, text, BigInteger
from sqlalchemy.orm import relationship, aliased
from datetime import datetime
from ...database import Base
from ..ilpuser.models import ILPUser
from ..block.models import Block
from ..district.models import District
from ..zone.models import Zone
from ..state.models import State

class School(Base):
    __tablename__ = "schools"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    long_name = Column(String)
    dise_code = Column(BigInteger, unique=True)
    block_id = Column(String, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False)
    address = Column(String)
    city = Column(String)
    pincode = Column(Integer)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships
    block = relationship("Block", backref="schools")
    classes = relationship("Class", back_populates="school", cascade="all, delete-orphan")
    
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
    
    @classmethod
    def get_school_details_fields(cls):
        """
        Dynamically extract valid fields based on SchoolDetailsResponse schema.
        Handles both model columns and relationships.
        """
        model_fields = cls.get_valid_fields()

        # Aliased models for relationships
        Block_alias = aliased(Block)
        District_alias = aliased(District)
        Zone_alias = aliased(Zone)
        State_alias = aliased(State)
        Creator = aliased(ILPUser)
        Updater = aliased(ILPUser)

        # Additional computed fields (from relationships)
        relation_mapping = {
            "block_name": Block_alias.name,
            "district_name": District_alias.name,
            "district_id": District_alias.id,
            "zone_id": Zone_alias.id,
            "zone_name": Zone_alias.name,
            "state_id": State_alias.id,
            "state_name": State_alias.name,
            "created_by": Creator.email,
            "updated_by": Updater.email,
        }

        model_fields.update(relation_mapping)

        return model_fields


class Class(Base):
    __tablename__ = "classes"

    id = Column(String, primary_key=True)
    grade = Column(String, nullable=False)
    section = Column(String)
    school_id = Column(String, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    last_updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow)

    created_by = Column(String, ForeignKey("ilp_users.id"))
    last_updated_by = Column(String, ForeignKey("ilp_users.id"))

    # Relationships
    school = relationship("School", back_populates="classes")
    
    creator = relationship("ILPUser", foreign_keys=[created_by])
    updater = relationship("ILPUser", foreign_keys=[last_updated_by])

    @classmethod
    def get_valid_fields(cls):
        return {column.name: column for column in cls.__table__.columns}
