# This file handles database models definition
# it defines Brand, Geo, Manager, Report, Fact classes with relationships

from sqlalchemy import (
    Column, Integer, String, Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Context: this class is used within the application to represent brands
# with their associated geos and managers
class Brand(Base):
    __tablename__ = "brand"
    id   = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    geos = relationship("Geo", back_populates="brand")

# Context: this class is used within the application to represent geographical regions
# associated with specific brands
class Geo(Base):
    __tablename__ = "geo"
    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("brand.id"), nullable=False)
    brand    = relationship("Brand", back_populates="geos")
    __table_args__ = (
        UniqueConstraint("name", "brand_id", name="uq_geo_brand"),
    )

# Context: this class is used within the application to represent managers
# associated with specific brands
class Manager(Base):
    __tablename__ = "manager"
    id       = Column(Integer, primary_key=True, index=True)
    tg_id    = Column(Integer, unique=True, nullable=False)
    name     = Column(String, nullable=False)
    brand_id = Column(Integer, ForeignKey("brand.id"), nullable=False)

# Context: this class is used within the application to represent daily reports
# with planned amounts for specific geos and dates
class Report(Base):
    __tablename__ = "report"
    id             = Column(Integer, primary_key=True, index=True)
    geo_id         = Column(Integer, ForeignKey("geo.id"), nullable=False)
    date           = Column(Date, nullable=False)
    amount_planned = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("geo_id", "date", name="uq_report_geo_date"),
    )

# Context: this class is used within the application to represent monthly facts
# with actual amounts for specific geos and months
class Fact(Base):
    __tablename__ = "fact"
    id          = Column(Integer, primary_key=True, index=True)
    geo_id      = Column(Integer, ForeignKey("geo.id"), nullable=False)
    month       = Column(String, nullable=False)  # формат "YYYY-MM"
    amount_fact = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint("geo_id", "month", name="uq_fact_geo_month"),
    )