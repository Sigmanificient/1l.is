from quart import Quart, render_template, request, redirect
import aiosqlite

from .base36 import base36_decode, base36_encode, base36_valid
from .database import fetch_single_item, get_db

QUERY_REDIRECT = "SELECT redirect FROM link WHERE id = ?"
QUERY_CHECK_ID = "SELECT name FROM link WHERE redirect = ?"
QUERY_INSERT_LINK = "INSERT INTO link(name, redirect) VALUES(?, ?)"
QUERY_LAST_ID = "SELECT IFNULL(id, 1) FROM link ORDER BY id desc LIMIT 1"


app = Quart(__name__)
app.config.update(DATABASE=app.root_path / ".." / ".." / ".db")


async def get_new_id(db: aiosqlite.Connection):
    last_id = await fetch_single_item(db, QUERY_LAST_ID, default=0)
    return base36_encode(last_id + 1)


@app.route("/")
async def home():
    return await render_template("index.jinja2")


@app.route("/<path:path>")
async def resolve_url(path: str):
    if not base36_valid(path):
        return f"Invalid url: {path}"

    url_id = base36_decode(path.lower())
    async with get_db(app) as db:
        url = await fetch_single_item(db, QUERY_REDIRECT, url_id, default='/')

    return redirect(url)


@app.route("/create", methods=["POST"])
async def create():
    form = await request.form
    url = form.get("url")
    if url is None:
        return "Invalid url"

    async with get_db(app) as db:
        res = await fetch_single_item(db, QUERY_CHECK_ID, url, default=None)

        if res is not None:
            return f"This url already exists: /{res}"

        name = await get_new_id(db)
        await db.execute_insert(QUERY_INSERT_LINK, (name, url))

    return f"Shorted url for {url}: /{name}"


def main():
    app.run()


if __name__ == "__main__":
    main()
