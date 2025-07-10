# This file handles daily workflow tests
# it defines test_duplicate_entry_blocked, test_jobs_scheduled functions

import pytest
from datetime import date
from services.crud import create_report, DuplicateReportError
from services.reports import get_today_summary, format_summary_markdown
from db.session import AsyncSessionLocal
from db.models import Office, Geo, Report

# Context: this function is used within the test suite to test duplicate report blocking
# and ensure data integrity is maintained
@pytest.mark.asyncio
async def test_duplicate_entry_blocked():
    """Test that duplicate reports are blocked by unique constraint"""
    import time
    
    # Create test data
    async with AsyncSessionLocal() as session:
        # Create test office with unique name using timestamp
        unique_name = f"Тестовий Офіс {int(time.time())}"
        office = Office(name=unique_name)
        session.add(office)
        await session.commit()
        
        # Create test geo
        geo = Geo(name=f"Тестовий Регіон {int(time.time())}", office_id=office.id)
        session.add(geo)
        await session.commit()
        
        # First report should succeed
        await create_report(
            office_id=office.id,
            geo_id=geo.id,
            report_date=date.today(),
            amount=1000
        )
        
        # Second report for same geo and date should fail
        with pytest.raises(DuplicateReportError):
            await create_report(
                office_id=office.id,
                geo_id=geo.id,
                report_date=date.today(),
                amount=2000
            )

# Context: this function is used within the test suite to test job queue scheduling
# and ensure daily tasks are properly configured
def test_jobs_scheduled():
    """Test that jobs are properly scheduled"""
    import os
    from dotenv import load_dotenv
    from telegram.ext import ApplicationBuilder, CommandHandler
    
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        bot_token = "dummy_token"
    
    app = ApplicationBuilder().token(bot_token).build()
    
    # Add handlers
    from handlers.start import start_command
    app.add_handler(CommandHandler("start", start_command))
    
    # Add jobs (same as in main.py)
    jq = app.job_queue
    
    # Monthly jobs
    from utils.schedule import next_last_day, next_first_day
    from main import ask_fact_all, monthly_report, dispatch_potential_prompts, send_admin_digest
    
    jq.run_once(ask_fact_all, when=next_last_day(19, 0))
    jq.run_once(monthly_report, when=next_first_day(9, 0))
    
    # Temporary testing jobs
    from datetime import timedelta
    jq.run_once(dispatch_potential_prompts, when=timedelta(seconds=10))
    jq.run_once(send_admin_digest, when=timedelta(seconds=60))
    
    # Check that jobs are scheduled
    jobs = jq.jobs()
    assert len(jobs) == 4  # 2 monthly + 2 temporary testing jobs
    
    # Check job names
    job_names = [job.name for job in jobs]
    assert "ask_fact_all" in job_names
    assert "monthly_report" in job_names
    assert "dispatch_potential_prompts" in job_names
    assert "send_admin_digest" in job_names

# Context: this function is used within the test suite to test summary formatting
# and ensure markdown is generated correctly
def test_format_summary_markdown():
    """Test that summary formatting works correctly"""
    # Test empty data
    empty_markdown = format_summary_markdown([])
    assert "немає даних" in empty_markdown
    
    # Test with data - create a simple mock object
    class MockRow:
        def __init__(self, office_name, geo_name, total_planned):
            self.office_name = office_name
            self.geo_name = geo_name
            self.total_planned = total_planned
    
    mock_data = [
        MockRow("Тестовий Офіс", "Тестовий Регіон", 1000)
    ]
    markdown = format_summary_markdown(mock_data)
    assert "Тестовий Офіс" in markdown
    assert "Тестовий Регіон" in markdown
    assert "1,000" in markdown 