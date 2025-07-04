# # This file handles JobQueue testing without full bot startup
# # it defines a test to verify job scheduling works correctly

# import os
# from datetime import time
# from dotenv import load_dotenv
# from telegram.ext import ApplicationBuilder

# # Context: this function is used within testing to verify JobQueue initialization
# # and job scheduling without running the full bot
# def test_jobqueue_setup():
#     """Test JobQueue setup and job scheduling"""
#     load_dotenv()
    
#     BOT_TOKEN = os.getenv("BOT_TOKEN")
#     if not BOT_TOKEN:
#         print("❌ BOT_TOKEN not found")
#         return
    
#     try:
#         # Create application
#         app = ApplicationBuilder().token(BOT_TOKEN).build()
        
#         # Check JobQueue availability
#         if app.job_queue is None:
#             print("❌ JobQueue is None - APScheduler not available")
#             return
        
#         print("✅ JobQueue is available")
        
#         # Define job functions (just for testing)
#         async def test_dispatch(context):
#             print("Test dispatch function called")
        
#         async def test_digest(context):
#             print("Test digest function called")
        
#         # Schedule jobs
#         jq = app.job_queue
        
#         # Schedule daily jobs
#         job1 = jq.run_daily(test_dispatch, time=time(18, 50))
#         job2 = jq.run_daily(test_digest, time=time(19, 30))
        
#         print("✅ Jobs scheduled successfully")
        
#         # Check jobs
#         jobs = list(jq.jobs())
#         print(f"📋 Total jobs: {len(jobs)}")
        
#         for i, job in enumerate(jobs, 1):
#             print(f"  {i}. {job.name} -> Next run: {job.job.next_run_time}")
        
#         # Check for expected jobs
#         job_names = [job.name for job in jobs]
#         expected = ['test_dispatch', 'test_digest']
        
#         print("\n✅ Expected jobs:")
#         for exp in expected:
#             status = "✅ FOUND" if exp in job_names else "❌ MISSING"
#             print(f"  {exp}: {status}")
        
#         # Clean up
#         job1.schedule_removal()
#         job2.schedule_removal()
        
#         print("\n🎯 JobQueue test completed successfully!")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")

# if __name__ == "__main__":
#     test_jobqueue_setup() 