from pathlib import Path
import aiosqlite
from contextlib import asynccontextmanager
from quart import Quart
from typing import AsyncGenerator


@asynccontextmanager
async def get_db(app: Quart) -> AsyncGenerator[aiosqlite.Connection, None]:
    db_path: Path = app.config["DATABASE"]

    if not db_path.exists():
        db_path.touch()

    db = await aiosqlite.connect(app.config["DATABASE"])
    yield db
    await db.close()
