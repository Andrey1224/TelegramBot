# This file handles test data creation
# it defines add_test_data function to populate database with sample data

import asyncio
import os
from dotenv import load_dotenv
from db.session import AsyncSessionLocal
from db.models import Office, Geo, User

# Context: this function is used within the test setup to create sample data
# for testing the daily workflow functionality
async def add_test_data():
    """Add test data to database for manual testing"""
    load_dotenv()
    
    admin_tg_id = os.getenv("ADMIN_TG_ID")
    if not admin_tg_id:
        print("❌ ADMIN_TG_ID not found in .env file!")
        return
    
    admin_tg_id = int(admin_tg_id)
    
    async with AsyncSessionLocal() as session:
        # Create test office
        office = Office(name="Тестовий Офіс")
        session.add(office)
        await session.commit()
        print(f"✅ Створено офіс: {office.name} (ID: {office.id})")
        
        # Create test geo
        geo = Geo(name="Київ", office_id=office.id)
        session.add(geo)
        await session.commit()
        print(f"✅ Створено регіон: {geo.name} (ID: {geo.id})")
        
        # Create test user (admin)
        user = User(
            tg_id=admin_tg_id,
            name="Тестовий Менеджер",
            office_id=office.id
        )
        session.add(user)
        await session.commit()
        print(f"✅ Створено користувача: {user.name} (TG ID: {user.tg_id})")
        
        print("\n🎉 Тестові дані успішно створено!")
        print(f"Офіс: {office.name} (ID: {office.id})")
        print(f"Регіон: {geo.name} (ID: {geo.id})")
        print(f"Користувач: {user.name} (TG ID: {user.tg_id})")
        print("\nТепер можна тестувати бота!")

if __name__ == "__main__":
    asyncio.run(add_test_data()) 