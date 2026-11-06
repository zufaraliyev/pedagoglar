import os
import asyncio
from seed_full_course import seed_full_database

async def seed_data():
    await seed_full_database()

if __name__ == "__main__":
    asyncio.run(seed_data())
