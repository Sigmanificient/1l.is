from quart import Quart, render_template

from .base36 import base36_decode, base36_encode, base36_valid
from .database import get_db

QUERY_REDIRECT = "SELECT redirect FROM link WHERE id = ?"
QUERY_CHECK_ID = "SELECT name FROM link WHERE redirect = ?"
QUERY_INSERT_LINK = "INSERT INTO link(name, redirect) VALUES(?, ?)"
QUERY_LAST_ID = "SELECT IFNULL(id, 1) FROM link ORDER BY id desc LIMIT 1"


app = Quart(__name__)
app.config.update(DATABASE=app.root_path / ".." / ".." / ".db")


@app.route("/")
async def home():
    return await render_template("index.jinja2")


@app.route("/create/<path:url>")
async def create(url: str):
    async with get_db(app) as db:
        res = tuple(await db.execute_fetchall(QUERY_CHECK_ID, (url,)))
        print(f"{res=!r}")

        if res:
            return res[0][0]

        last_id = (
            tuple(await db.execute_fetchall(QUERY_LAST_ID, ()))
            or ((0,),)
        )[0][0]

        print(f"{last_id=!r}")

        name = base36_encode(last_id + 1)
        print(f"{name=!r}")

        await db.execute(QUERY_INSERT_LINK, (name, url))
        await db.commit()

    return name


@app.route("/<path:path>")
async def resolve_url(path: str):
    if not base36_valid(path):
        return f"Invalid url: {path}"
    url_id = base36_decode(path.lower())
    print(url_id)

    async with get_db(app) as db:
        redirect = tuple(await db.execute_fetchall(QUERY_REDIRECT, (url_id,)))

    return str(redirect)

def main():
    app.run()


if __name__ == "__main__":
    main()
