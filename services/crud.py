# This file handles database CRUD operations
# it defines create_report, get_users_by_geo, get_geo_by_office functions

from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from datetime import date
from db.models import Report, User, Geo, Office
from db.session import AsyncSessionLocal
from utils.logger import logger

class DuplicateReportError(Exception):
    """Raised when trying to create a duplicate report for the same geo and date"""
    pass

# Context: this function is used within the application to create new daily reports
# and handle duplicate entries gracefully
async def create_report(office_id: int, geo_id: int, report_date: date, amount: int):
    """Create a new daily report for specific geo and date"""
    async with AsyncSessionLocal() as session:
        report = Report(
            office_id=office_id,
            geo_id=geo_id, 
            date=report_date, 
            amount_planned=amount
        )
        session.add(report)
        try:
            await session.commit()
            logger.info("Saved planned amount for office=%s geo=%s sum=%d", office_id, geo_id, amount)
        except IntegrityError:
            await session.rollback()
            logger.warning("Duplicate report attempt for office=%s geo=%s date=%s", office_id, geo_id, report_date)
            raise DuplicateReportError(f"Report for geo {geo_id} on {report_date} already exists")

# Context: this function is used within the application to get all users
# associated with specific geos for daily prompts
async def get_users_by_geo():
    """Get all users grouped by their office's geos"""
    async with AsyncSessionLocal() as session:
        query = (
            select(User, Geo, Office)
            .join(Office, User.office_id == Office.id)
            .join(Geo, Geo.office_id == Office.id)
        )
        result = await session.execute(query)
        return result.all()

# Context: this function is used within the application to get all geos
# for a specific office for reporting purposes
async def get_geo_by_office(office_id: int):
    """Get all geos for a specific office"""
    async with AsyncSessionLocal() as session:
        query = select(Geo).where(Geo.office_id == office_id)
        result = await session.execute(query)
        return result.scalars().all()