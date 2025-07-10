# This file handles tests for monthly workflow functionality
# it defines test cases for edge dates, schedule functions, and monthly handlers

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import patch
from utils.schedule import next_last_day, next_first_day, current_month_date, previous_month_date
import pytz

class TestEdgeDates:
    """Test edge cases for date calculations"""
    
    def test_april_30_last_day(self):
        """Test last day calculation for April (30 days)"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as April 15, 2025 at 10:00
            mock_datetime.now.return_value = datetime(2025, 4, 15, 10, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result = next_last_day(19, 0)
            
            # Should return April 30, 2025 at 19:00
            assert result.day == 30
            assert result.month == 4
            assert result.year == 2025
            assert result.hour == 19
            assert result.minute == 0
    
    def test_february_leap_year(self):
        """Test February 29 in leap year"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as February 15, 2024 (leap year)
            mock_datetime.now.return_value = datetime(2024, 2, 15, 10, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result = next_last_day(19, 0)
            
            # Should return February 29, 2024 at 19:00
            assert result.day == 29
            assert result.month == 2
            assert result.year == 2024
            assert result.hour == 19
            assert result.minute == 0
    
    def test_february_non_leap_year(self):
        """Test February 28 in non-leap year"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as February 15, 2025 (non-leap year)
            mock_datetime.now.return_value = datetime(2025, 2, 15, 10, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result = next_last_day(19, 0)
            
            # Should return February 28, 2025 at 19:00
            assert result.day == 28
            assert result.month == 2
            assert result.year == 2025
            assert result.hour == 19
            assert result.minute == 0
    
    def test_december_31_to_january_1(self):
        """Test transition from December 31 to January 1"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as December 31, 2024 at 20:00 (after 19:00)
            mock_datetime.now.return_value = datetime(2024, 12, 31, 20, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result_last = next_last_day(19, 0)
            result_first = next_first_day(9, 0)
            
            # next_last_day should return January 31, 2025 (next month's last day)
            assert result_last.day == 31
            assert result_last.month == 1
            assert result_last.year == 2025
            
            # next_first_day should return January 1, 2025
            assert result_first.day == 1
            assert result_first.month == 1
            assert result_first.year == 2025
    
    def test_march_31_edge_case(self):
        """Test March 31 edge case"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as March 31, 2025 at 18:00 (before 19:00)
            mock_datetime.now.return_value = datetime(2025, 3, 31, 18, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result = next_last_day(19, 0)
            
            # Should return March 31, 2025 at 19:00 (same day)
            assert result.day == 31
            assert result.month == 3
            assert result.year == 2025
            assert result.hour == 19
            assert result.minute == 0
    
    def test_first_day_edge_case(self):
        """Test first day calculation when already on 1st"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as January 1, 2025 at 08:00 (before 09:00)
            mock_datetime.now.return_value = datetime(2025, 1, 1, 8, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result = next_first_day(9, 0)
            
            # Should return January 1, 2025 at 09:00 (same day)
            assert result.day == 1
            assert result.month == 1
            assert result.year == 2025
            assert result.hour == 9
            assert result.minute == 0
    
    def test_first_day_after_time_passed(self):
        """Test first day calculation when time already passed"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time as January 1, 2025 at 10:00 (after 09:00)
            mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 0, 0, tzinfo=pytz.timezone('Europe/Kyiv'))
            
            result = next_first_day(9, 0)
            
            # Should return February 1, 2025 at 09:00 (next month)
            assert result.day == 1
            assert result.month == 2
            assert result.year == 2025
            assert result.hour == 9
            assert result.minute == 0

class TestMonthDateFunctions:
    """Test month date utility functions"""
    
    def test_current_month_date(self):
        """Test current_month_date returns first day of current month"""
        with patch('utils.schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 15, 10, 0, 0)
            
            result = current_month_date()
            
            assert result == date(2025, 7, 1)
    
    def test_previous_month_date(self):
        """Test previous_month_date returns first day of previous month"""
        with patch('utils.schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 15, 10, 0, 0)
            
            result = previous_month_date()
            
            assert result == date(2025, 6, 1)
    
    def test_previous_month_date_january(self):
        """Test previous_month_date when current month is January"""
        with patch('utils.schedule.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 15, 10, 0, 0)
            
            result = previous_month_date()
            
            assert result == date(2024, 12, 1)

class TestTimezoneHandling:
    """Test timezone handling in schedule functions"""
    
    def test_timezone_consistency(self):
        """Test that all functions use Europe/Kyiv timezone consistently"""
        with patch('utils.schedule.datetime') as mock_datetime:
            # Mock current time in Europe/Kyiv
            kyiv_tz = pytz.timezone('Europe/Kyiv')
            mock_datetime.now.return_value = datetime(2025, 7, 15, 10, 0, 0, tzinfo=kyiv_tz)
            
            # Test that functions use the specified timezone
            result = next_last_day(19, 0, "Europe/Kyiv")
            
            # Should be in Europe/Kyiv timezone
            assert result.tzinfo.zone == "Europe/Kyiv"
    
    def test_different_timezones(self):
        """Test schedule functions with different timezones"""
        # Test Europe/Kyiv
        with patch('utils.schedule.datetime') as mock_datetime:
            kyiv_tz = pytz.timezone('Europe/Kyiv')
            mock_datetime.now.return_value = datetime(2025, 7, 15, 10, 0, 0, tzinfo=kyiv_tz)
            
            result_kyiv = next_last_day(19, 0, "Europe/Kyiv")
            assert result_kyiv.tzinfo.zone == "Europe/Kyiv"
        
        # Test UTC
        with patch('utils.schedule.datetime') as mock_datetime:
            utc_tz = pytz.UTC
            mock_datetime.now.return_value = datetime(2025, 7, 15, 10, 0, 0, tzinfo=utc_tz)
            
            result_utc = next_last_day(19, 0, "UTC")
            assert result_utc.tzinfo.zone == "UTC"

def test_timezone_handling_in_utc():
    """Test that timezone handling works correctly even when system is in UTC"""
    import os
    import tempfile
    
    # Temporarily set TZ to UTC to simulate Docker environment
    original_tz = os.environ.get('TZ')
    os.environ['TZ'] = 'UTC'
    
    try:
        # Import after setting TZ to ensure it uses UTC
        from utils.schedule import next_first_day, next_last_day
        from datetime import datetime
        import pytz
        
        # Test that functions still return Kyiv time even in UTC environment
        kyiv_tz = pytz.timezone('Europe/Kiev')
        
        # Test next_first_day
        first_day = next_first_day(9, 0)
        first_day_kyiv = first_day.astimezone(kyiv_tz)
        
        assert first_day_kyiv.hour == 9
        assert first_day_kyiv.day == 1
        
        # Test next_last_day
        last_day = next_last_day(19, 0)
        last_day_kyiv = last_day.astimezone(kyiv_tz)
        
        assert last_day_kyiv.hour == 19
        # Should be last day of month
        next_month = last_day_kyiv.replace(day=28) + timedelta(days=4)
        last_day_of_month = next_month - timedelta(days=next_month.day)
        assert last_day_kyiv.day == last_day_of_month.day
        
    finally:
        # Restore original TZ
        if original_tz:
            os.environ['TZ'] = original_tz
        elif 'TZ' in os.environ:
            del os.environ['TZ']

def test_parse_amount():
    """Test amount parsing with various formats"""
    from utils.logger import parse_amount
    
    # Test valid formats
    assert parse_amount("1000") == (1000, "")
    assert parse_amount("1 000") == (1000, "")
    assert parse_amount("1,000") == (1000, "")  # Thousands separator
    assert parse_amount("1000.00") == (1000, "")  # Decimal
    assert parse_amount("1 000,50") == (1000, "")  # Comma treated as thousands separator
    assert parse_amount("1000,50") == (1000, "")  # Comma as decimal separator (rounded down)
    assert parse_amount("1000.50") == (1000, "")  # Decimal separator (rounded down)
    assert parse_amount("1000.75") == (1001, "")  # Decimal separator (rounded up)
    assert parse_amount("1,000.50") == (1000, "")  # US format (rounded down)
    assert parse_amount("12 345 678") == (12345678, "")
    
    # Test with emojis and special characters
    assert parse_amount("💰 1000 ₴") == (1000, "")
    assert parse_amount("1000₴") == (1000, "")
    
    # Test error cases
    assert parse_amount("")[1] != ""  # Empty string
    assert parse_amount("-1000")[1] != ""  # Negative
    assert parse_amount("abc")[1] != ""  # Non-numeric
    assert parse_amount("1000000000000")[1] != ""  # Too large

def test_telegram_retry_functionality():
    """Test telegram retry decorator basic functionality"""
    from utils.logger import telegram_retry
    import asyncio
    
    # Test successful execution
    @telegram_retry(max_retries=2)
    async def success_func():
        return "success"
    
    async def run_test():
        result = await success_func()
        assert result == "success"
    
    asyncio.run(run_test())

def test_cancel_handler_logic():
    """Test cancel handler state management"""
    from handlers.start import cancel_handler
    from unittest.mock import AsyncMock, MagicMock
    import asyncio
    
    # Mock update and context
    update = MagicMock()
    update.effective_user.id = 123
    update.message.reply_text = AsyncMock()
    
    context = MagicMock()
    context.user_data = {'waiting_for_fact': True}
    
    # Test with active state
    result = asyncio.run(cancel_handler(update, context))
    update.message.reply_text.assert_called_once()
    assert "скасовано" in update.message.reply_text.call_args[0][0]

if __name__ == "__main__":
    pytest.main([__file__]) 