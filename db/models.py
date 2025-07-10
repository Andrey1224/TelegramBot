# This file handles database models
# it defines Office, Geo, User, Report, Fact classes using SQLAlchemy ORM

from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Office(Base):
    __tablename__ = 'offices'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    # Relationships
    geos = relationship("Geo", back_populates="office")
    users = relationship("User", back_populates="office")
    reports = relationship("Report", back_populates="office")

class Geo(Base):
    __tablename__ = 'geo'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    office_id = Column(Integer, ForeignKey('offices.id'), nullable=False)
    
    # Relationships
    office = relationship("Office", back_populates="geos")
    reports = relationship("Report", back_populates="geo")
    facts = relationship("Fact", back_populates="geo")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False, unique=True)
    name = Column(String, nullable=False)
    office_id = Column(Integer, ForeignKey('offices.id'), nullable=False)
    
    # Relationships
    office = relationship("Office", back_populates="users")

class Report(Base):
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    office_id = Column(Integer, ForeignKey('offices.id'), nullable=False)
    geo_id = Column(Integer, ForeignKey('geo.id'), nullable=False)
    date = Column(Date, nullable=False)
    amount_planned = Column(Integer, nullable=False)
    
    # Relationships
    office = relationship("Office", back_populates="reports")
    geo = relationship("Geo", back_populates="reports")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('geo_id', 'date', name='uq_report_geo_date'),)

class Fact(Base):
    __tablename__ = 'facts'
    
    id = Column(Integer, primary_key=True)
    geo_id = Column(Integer, ForeignKey('geo.id'), nullable=False)
    month = Column(Date, nullable=False)  # Changed from String to Date - stores first day of month
    amount_fact = Column(Integer, nullable=False)
    
    # Relationships
    geo = relationship("Geo", back_populates="facts")
    
    # Unique constraint
    __table_args__ = (UniqueConstraint('geo_id', 'month', name='uq_fact_geo_month'),)


# Backward compatibility aliases for existing code
Brand = Office
Manager = User

# Export all models
__all__ = ["Office", "Geo", "User", "Report", "Fact", "Brand", "Manager", "Base"]