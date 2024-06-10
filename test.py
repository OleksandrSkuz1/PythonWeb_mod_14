import asyncpg
import asyncio

async def test_connection():
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='567234',
            database='rest_app',
            host='localhost',
            port=5432
        )
        print("Connection to PostgreSQL successful!")
        await conn.close()
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")

asyncio.run(test_connection())
