# This file handles schedule utility functions
# it defines next_last_day, next_first_day, current_month_date, previous_month_date functions

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import pytz

def next_last_day(hour: int, minute: int, timezone: str = "Europe/Kyiv"):
    """Calculate next last day of month at specified time"""
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    # Get last day of current month
    next_month = now.replace(day=1) + relativedelta(months=1)
    last_day = next_month - relativedelta(days=1)
    
    # Set target time
    target_time = last_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # If target time already passed, move to next month
    if target_time <= now:
        # Get last day of next month
        next_next_month = next_month + relativedelta(months=1)
        last_day = next_next_month - relativedelta(days=1)
        target_time = last_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return target_time

def next_first_day(hour: int, minute: int, timezone: str = "Europe/Kyiv"):
    """Calculate next first day of month at specified time"""
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    
    # Get first day of current month
    first_day_current = now.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
    
    # If we haven't reached the target time today and we're on the 1st, use today
    if now.day == 1 and first_day_current > now:
        return first_day_current
    
    # Otherwise, get first day of next month
    next_month = now.replace(day=1) + relativedelta(months=1)
    target_time = next_month.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    return target_time

def current_month_date():
    """Get current month as Date object (first day of month)"""
    now = datetime.now()
    return now.replace(day=1).date()

def previous_month_date():
    """Get previous month as Date object (first day of previous month)"""
    now = datetime.now()
    prev_month = now.replace(day=1) - relativedelta(months=1)
    return prev_month.date()

def current_month_string():
    """Get current month as string in YYYY-MM format (backward compatibility)"""
    now = datetime.now()
    return now.strftime("%Y-%m")

def previous_month_string():
    """Get previous month as string in YYYY-MM format (backward compatibility)"""
    now = datetime.now()
    prev_month = now - relativedelta(months=1)
    return prev_month.strftime("%Y-%m") 