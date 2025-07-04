# # Файл полностью закомментирован для Milestone 2 — не участвует в тестировании ежедневного workflow
# # This file handles manual function testing
# # it defines test_dispatch and test_digest functions for manual testing

# import asyncio
# import os
# from dotenv import load_dotenv
# from handlers.daily import dispatch_potential_prompts, send_admin_digest
# from utils.logger import logger

# # Context: this function is used within manual testing to invoke dispatch function
# # and test the daily prompt sending functionality
# async def test_dispatch():
#     """Test dispatch_potential_prompts function manually"""
#     print("🧪 Testing dispatch_potential_prompts...")
    
#     try:
#         # Create a mock context (we don't need real bot context for this test)
#         class MockContext:
#             def __init__(self):
#                 self.bot = None
        
#         context = MockContext()
        
#         await dispatch_potential_prompts(context)
#         print("✅ dispatch_potential_prompts completed successfully!")
        
#     except Exception as e:
#         print(f"❌ Error in dispatch_potential_prompts: {e}")
#         logger.error("Test dispatch failed: %s", str(e))

# # Context: this function is used within manual testing to invoke digest function
# # and test the admin digest sending functionality
# async def test_digest():
#     """Test send_admin_digest function manually"""
#     print("🧪 Testing send_admin_digest...")
    
#     try:
#         # Create a mock context
#         class MockContext:
#             def __init__(self):
#                 self.bot = None
        
#         context = MockContext()
        
#         await send_admin_digest(context)
#         print("✅ send_admin_digest completed successfully!")
        
#     except Exception as e:
#         print(f"❌ Error in send_admin_digest: {e}")
#         logger.error("Test digest failed: %s", str(e))

# # Context: this function is used within manual testing to run both test functions
# # and provide a comprehensive testing interface
# async def run_tests():
#     """Run both test functions"""
#     load_dotenv()
    
#     print("🚀 Starting manual function tests...\n")
    
#     # Test dispatch
#     await test_dispatch()
#     print()
    
#     # Test digest
#     await test_digest()
#     print()
    
#     print("🎉 All tests completed!")

# if __name__ == "__main__":
#     asyncio.run(run_tests()) 