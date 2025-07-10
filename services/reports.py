# This file handles report generation and formatting
# it defines format_daily_digest and generate_monthly_report functions

from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select, func, extract
from datetime import date
from db.models import Geo, Report, Office, Fact
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

# Context: this function is used within the application to get monthly summary
# comparing planned vs actual amounts for specific month
async def get_monthly_summary(month: str):
    """Get monthly summary with planned vs actual amounts by geo"""
    
    # Convert string month to date object for comparison
    month_date = datetime.strptime(month, "%Y-%m").date().replace(day=1)
    
    async with AsyncSessionLocal() as session:
        # Get planned amounts (sum of daily reports for the month)
        planned_query = (
            select(
                Office.name.label('office_name'),
                Geo.name.label('geo_name'),
                Geo.id.label('geo_id'),
                func.sum(Report.amount_planned).label('total_planned')
            )
            .select_from(Report)
            .join(Geo, Report.geo_id == Geo.id)
            .join(Office, Report.office_id == Office.id)
            .where(extract('year', Report.date) == month_date.year)
            .where(extract('month', Report.date) == month_date.month)
            .group_by(Office.name, Geo.name, Geo.id)
        )
        
        # Get actual amounts (facts for the month)
        actual_query = (
            select(
                Geo.id.label('geo_id'),
                Fact.amount_fact.label('amount_fact')
            )
            .select_from(Fact)
            .join(Geo, Fact.geo_id == Geo.id)
            .where(Fact.month == month_date)
        )
        
        planned_result = await session.execute(planned_query)
        actual_result = await session.execute(actual_query)
        
        # Convert to dictionaries for easier processing
        planned_data = {row.geo_id: row for row in planned_result.all()}
        actual_data = {row.geo_id: row.amount_fact for row in actual_result.all()}
        
        # Combine data
        summary = []
        for geo_id, planned_row in planned_data.items():
            actual_amount = actual_data.get(geo_id, 0)
            
            summary.append({
                'office_name': planned_row.office_name,
                'geo_name': planned_row.geo_name,
                'geo_id': geo_id,
                'total_planned': planned_row.total_planned,
                'amount_fact': actual_amount,
                'delta': actual_amount - planned_row.total_planned,
                'delta_percent': ((actual_amount - planned_row.total_planned) / planned_row.total_planned * 100) if planned_row.total_planned > 0 else 0
            })
        
        return summary

# Context: this function is used within the application to get monthly delta
# calculation for specific month showing plan vs fact comparison
async def get_monthly_delta(month: str):
    """Get monthly delta calculation showing plan vs fact comparison"""
    summary = await get_monthly_summary(month)
    
    if not summary:
        return {
            'total_planned': 0,
            'total_fact': 0,
            'total_delta': 0,
            'total_delta_percent': 0,
            'geos_count': 0,
            'geos_with_facts': 0
        }
    
    total_planned = sum(item['total_planned'] for item in summary)
    total_fact = sum(item['amount_fact'] for item in summary)
    total_delta = total_fact - total_planned
    total_delta_percent = (total_delta / total_planned * 100) if total_planned else 0
    
    geos_count = len(summary)
    geos_with_facts = sum(1 for item in summary if item['amount_fact'] > 0)
    
    return {
        'total_planned': total_planned,
        'total_fact': total_fact,
        'total_delta': total_delta,
        'total_delta_percent': total_delta_percent,
        'geos_count': geos_count,
        'geos_with_facts': geos_with_facts,
        'details': summary
    }

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

# Context: this function is used within the application to format monthly report
# into markdown table for admin with plan vs fact comparison
def format_monthly_report_markdown(delta_data, month: str):
    """Format monthly report data into markdown table with delta analysis"""
    if not delta_data or not delta_data.get('details'):
        return f"📊 **Місячний звіт за {month}**\n\n❌ Немає даних для звіту"
    
    details = delta_data['details']
    
    markdown = f"📊 **Місячний звіт за {month}**\n\n"
    markdown += "| Офіс | Регіон | План | Факт | Δ | Δ % |\n"
    markdown += "|------|--------|------|------|---|-----|\n"
    
    for item in details:
        office_name = item['office_name'] or "Невідомий офіс"
        geo_name = item['geo_name'] or "Невідомий регіон"
        planned = item['total_planned']
        fact = item['amount_fact']
        delta = item['delta']
        delta_percent = item['delta_percent']
        
        # Handle missing facts
        if fact == 0:
            fact_str = "—"
            delta_str = "⚠️ Немає даних"
            percent_str = "—"
        else:
            fact_str = f"{fact:,} ₴"
            delta_icon = "📈" if delta > 0 else "📉" if delta < 0 else "➖"
            delta_str = f"{delta_icon} {delta:+,} ₴"
            percent_str = f"{delta_percent:+.1f}%"
        
        markdown += f"| {office_name} | {geo_name} | {planned:,} ₴ | {fact_str} | {delta_str} | {percent_str} |\n"
    
    # Summary section
    total_planned = delta_data['total_planned']
    total_fact = delta_data['total_fact']
    total_delta = delta_data['total_delta']
    total_delta_percent = delta_data['total_delta_percent']
    geos_count = delta_data['geos_count']
    geos_with_facts = delta_data['geos_with_facts']
    geos_missing = geos_count - geos_with_facts
    
    summary_icon = "📈" if total_delta > 0 else "📉" if total_delta < 0 else "➖"
    
    markdown += f"\n**📋 Підсумок:**\n"
    markdown += f"• План: {total_planned:,} ₴\n"
    markdown += f"• Факт: {total_fact:,} ₴\n"
    markdown += f"• Дельта: {summary_icon} {total_delta:+,} ₴ ({total_delta_percent:+.1f}%)\n"
    markdown += f"• Регіонів з фактами: {geos_with_facts}/{geos_count}\n"
    
    if geos_missing > 0:
        markdown += f"• ⚠️ Не відповіли: {geos_missing} регіонів\n"
    
    return markdown

# Context: this function is used within the application to generate monthly reports
# comparing planned vs actual amounts for all GEOs
async def generate_monthly_report(session, target_month: str) -> str:
    """Generate monthly report comparing plan vs fact for all GEOs"""
    from sqlalchemy import text
    
    # Convert target_month to date format for comparison
    target_date = datetime.strptime(target_month, "%Y-%m").date()
    
    # Get all GEOs with their office names and calculate totals
    query = text("""
        SELECT 
            g.id,
            g.name as geo_name,
            o.name as office_name,
            COALESCE(SUM(r.amount_plan), 0) as total_plan,
            COALESCE(f.amount_fact, 0) as total_fact
        FROM geo g
        JOIN office o ON g.office_id = o.id
        LEFT JOIN report r ON g.id = r.geo_id 
            AND strftime('%Y-%m', r.date) = :target_month
        LEFT JOIN fact f ON g.id = f.geo_id 
            AND f.month = :target_date
        GROUP BY g.id, g.name, o.name, f.amount_fact
        ORDER BY o.name, g.name
    """)
    
    result = await session.execute(query, {
        'target_month': target_month,
        'target_date': target_date
    })
    rows = result.fetchall()
    
    if not rows:
        return f"📊 Звіт за {target_month}\n\n❌ Дані відсутні"
    
    # Group by office for better formatting
    offices = {}
    total_plan = 0
    total_fact = 0
    missing_geos = []  # Track GEOs without facts
    
    for row in rows:
        geo_id, geo_name, office_name, plan, fact = row
        
        if office_name not in offices:
            offices[office_name] = []
        
        offices[office_name].append({
            'geo_name': geo_name,
            'plan': plan,
            'fact': fact
        })
        
        total_plan += plan
        total_fact += fact
        
        # Track missing facts
        if fact == 0:
            missing_geos.append(f"{office_name}: {geo_name}")
    
    # Build report
    report_lines = [f"📊 Звіт за {target_month}"]
    
    for office_name, geos in offices.items():
        report_lines.append(f"\n🏢 {office_name}")
        
        for geo in geos:
            plan_str = f"{geo['plan']:,}".replace(',', ' ')
            
            if geo['fact'] > 0:
                fact_str = f"{geo['fact']:,}".replace(',', ' ')
                percentage = (geo['fact'] / geo['plan'] * 100) if geo['plan'] > 0 else 0
                status = "✅" if percentage >= 100 else "⚠️" if percentage >= 80 else "❌"
                report_lines.append(f"  {status} {geo['geo_name']}: {plan_str} → {fact_str} ({percentage:.1f}%)")
            else:
                report_lines.append(f"  — {geo['geo_name']}: {plan_str} → немає даних")
    
    # Summary
    plan_str = f"{total_plan:,}".replace(',', ' ')
    fact_str = f"{total_fact:,}".replace(',', ' ')
    total_percentage = (total_fact / total_plan * 100) if total_plan > 0 else 0
    
    report_lines.append(f"\n📈 Загальний підсумок:")
    report_lines.append(f"План: {plan_str}")
    report_lines.append(f"Факт: {fact_str}")
    report_lines.append(f"Виконання: {total_percentage:.1f}%")
    
    # Add details about missing responses
    if missing_geos:
        report_lines.append(f"\n⚠️ Не відповіли ({len(missing_geos)} регіонів):")
        for missing_geo in missing_geos:
            report_lines.append(f"  • {missing_geo}")
    
    return "\n".join(report_lines)