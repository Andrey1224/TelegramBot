# # Файл полностью закомментирован для Milestone 2 — не участвует в тестировании ежедневного workflow
# # This file handles database function testing
# # it defines test functions for CRUD operations and report generation

# import asyncio
# import os
# from datetime import date
# from dotenv import load_dotenv
# from db.session import AsyncSessionLocal
# from services.crud import create_report
# from services.reports import get_today_summary, format_summary_markdown

# # Context: this function is used within testing to verify database operations
# # and report generation functionality
# async def test_db_functions():
#     """Test database functions manually"""
#     load_dotenv()
    
#     print("🧪 Testing database functions...")
    
#     async with AsyncSessionLocal() as session:
#         try:
#             # Test creating a new report
#             print("\n1. Creating test report...")
#             await create_report(office_id=1, geo_id=7, report_date=date.today(), amount=2500)
#             print("✅ Report created successfully!")
            
#             # Test duplicate prevention
#             print("\n2. Testing duplicate prevention...")
#             try:
#                 await create_report(office_id=1, geo_id=7, report_date=date.today(), amount=3000)
#                 print("❌ Duplicate should have been blocked!")
#             except Exception as e:
#                 print(f"✅ Duplicate blocked: {e}")
            
#             # Test getting today's summary
#             print("\n3. Getting today's summary...")
#             summary = await get_today_summary(session)
#             print(f"✅ Summary: {summary}")
            
#             # Test markdown formatting
#             print("\n4. Testing markdown formatting...")
#             markdown = format_summary_markdown(summary)
#             print("✅ Markdown table:")
#             print(markdown)
            
#         except Exception as e:
#             print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     asyncio.run(test_db_functions()) 