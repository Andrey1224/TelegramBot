# This file handles report calculations and summaries
# it defines get_today_summary, get_office_summary functions

from sqlalchemy import select, func
from datetime import date
from db.models import Geo, Report, Office
from db.session import AsyncSessionLocal
from utils.logger import logger

# Context: this function is used within the application to get daily summary
# of all planned amounts grouped by geo for admin digest
async def get_today_summary():
    """Get today's summary of planned amounts by geo"""
    today = date.today()
    async with AsyncSessionLocal() as session:
        query = (
            select(
                Office.name.label("office_name"),
                Geo.name.label("geo_name"), 
                func.sum(Report.amount_planned).label("total_planned")
            )
            .join(Report, Geo.id == Report.geo_id)
            .join(Office, Report.office_id == Office.id)
            .where(Report.date == today)
            .group_by(Office.id, Geo.id)
            .order_by(Office.name, Geo.name)
        )
        result = await session.execute(query)
        return result.all()

# Context: this function is used within the application to get summary
# for a specific office with all its geos
async def get_office_summary(office_id: int, report_date: date | None = None):
    """Get summary for specific office on specific date (defaults to today)"""
    if report_date is None:
        report_date = date.today()
    async with AsyncSessionLocal() as session:
        query = (
            select(
                Geo.name.label("geo_name"),
                func.sum(Report.amount_planned).label("total_planned")
            )
            .join(Report, Geo.id == Report.geo_id)
            .where(Report.office_id == office_id, Report.date == report_date)
            .group_by(Geo.id)
            .order_by(Geo.name)
        )
        result = await session.execute(query)
        return result.all()

# Context: this function is used within the application to format summary data
# into markdown table for admin digest
def format_summary_markdown(summary_data):
    """Format summary data into markdown table"""
    if not summary_data:
        return "📊 **Сьогодні немає даних про плановий прибуток**"
    
    markdown = "📊 **Щоденний дайджест планового прибутку**\n\n"
    markdown += "| Офіс | Регіон | Планова сума |\n"
    markdown += "|------|--------|-------------|\n"
    
    for row in summary_data:
        office_name = row.office_name or "Невідомий офіс"
        geo_name = row.geo_name or "Невідомий регіон"
        amount = row.total_planned or 0
        markdown += f"| {office_name} | {geo_name} | {amount:,} ₴ |\n"
    
    total_sum = sum(row.total_planned or 0 for row in summary_data)
    markdown += f"\n**Разом: {total_sum:,} ₴**"
    
    return markdown