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
@pytest.mark.asyncio
async def test_jobs_scheduled():
    """Test that job queue has exactly 2 daily jobs scheduled"""
    from main import app
    
    # Check that job queue exists
    assert app.job_queue is not None
    
    # Get all jobs
    jobs = app.job_queue.jobs()
    
    # Should have exactly 2 jobs
    assert len(jobs) == 2
    
    # Check job names (they should be our daily functions)
    job_names = [job.name for job in jobs]
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