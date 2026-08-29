"""Allow prescriptions created directly from a diagnosis record."""
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database import engine


async def main():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE prescriptions ALTER COLUMN consultation_id DROP NOT NULL"))
    print("prescriptions.consultation_id is now nullable")


if __name__ == "__main__":
    asyncio.run(main())
