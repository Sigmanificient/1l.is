from pathlib import Path
import aiosqlite
from contextlib import asynccontextmanager
from functools import wraps
from quart import Quart
from typing import AsyncGenerator, Optional


def _singleton(gfunc):
    db: Optional[aiosqlite.Connection] = None

    @wraps(gfunc)
    async def wrapped(*args):
        nonlocal db

        if db is None or not db.is_alive():
            db = await gfunc(*args).__anext__()

        yield db

    return wrapped

@asynccontextmanager
@_singleton
async def get_db(app: Quart) -> AsyncGenerator[aiosqlite.Connection, None]:
    db_path: Path = app.config["DATABASE"]

    if not db_path.exists():
        db_path.touch()

    db = await aiosqlite.connect(app.config["DATABASE"])
    yield db
    await db.close()



async def fetch_single_item(db, query, *params, default):
    cursor = await db.execute(query, params)
    row = await cursor.fetchone()

    return row[0] if row else default
