# This file handles database models definition
# it defines Brand, Geo, Manager, Report, Fact classes with relationships

from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Context: this class is used within the application to represent offices
# with their associated geos and users
class Office(Base):
    __tablename__ = "offices"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    geos = relationship("Geo", back_populates="office")
    users = relationship("User", back_populates="office")
    reports = relationship("Report", back_populates="office")

# Context: this class is used within the application to represent geographical regions
# associated with specific offices
class Geo(Base):
    __tablename__ = "geo"
    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, nullable=False)
    office_id = Column(Integer, ForeignKey("offices.id"), nullable=False)
    office    = relationship("Office", back_populates="geos")
    reports   = relationship("Report", back_populates="geo")
    facts     = relationship("Fact", back_populates="geo")
    __table_args__ = (
        UniqueConstraint("name", "office_id", name="uq_geo_office"),
    )

# Context: this class is used within the application to represent users
# associated with specific offices
class User(Base):
    __tablename__ = "users"
    id        = Column(Integer, primary_key=True, index=True)
    tg_id     = Column(Integer, unique=True, nullable=False)
    name      = Column(String, nullable=False)
    office_id = Column(Integer, ForeignKey("offices.id"), nullable=False)
    office    = relationship("Office", back_populates="users")

# Context: this class is used within the application to represent daily reports
# with planned amounts for specific geos and dates
class Report(Base):
    __tablename__ = "reports"
    id             = Column(Integer, primary_key=True, index=True)
    office_id      = Column(Integer, ForeignKey("offices.id"), nullable=False)
    geo_id         = Column(Integer, ForeignKey("geo.id"), nullable=False)
    date           = Column(Date, nullable=False)
    amount_planned = Column(Integer, nullable=False)
    office         = relationship("Office", back_populates="reports")
    geo            = relationship("Geo", back_populates="reports")
    __table_args__ = (
        UniqueConstraint("office_id", "geo_id", "date", name="uq_report_office_geo_date"),
    )

# Context: this class is used within the application to represent monthly facts
# with actual amounts for specific geos and months
class Fact(Base):
    __tablename__ = "facts"
    id          = Column(Integer, primary_key=True, index=True)
    geo_id      = Column(Integer, ForeignKey("geo.id"), nullable=False)
    month       = Column(String, nullable=False)  # формат "YYYY-MM"
    amount_fact = Column(Integer, nullable=False)
    geo         = relationship("Geo", back_populates="facts")
    __table_args__ = (
        UniqueConstraint("geo_id", "month", name="uq_fact_geo_month"),
    )


# Backward compatibility aliases for existing code
Brand = Office
Manager = User

# Export all models
__all__ = ["Office", "Geo", "User", "Report", "Fact", "Brand", "Manager", "Base"]