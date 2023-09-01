from quart import Quart

from .database import get_db

app = Quart(__name__)
app.config.update(DATABASE=app.root_path / ".." / ".." / ".db")


@app.route("/")
async def home():
    script = (app.root_path / ".." / ".." / "seeder.sql").read_text()

    async with get_db(app) as db:
        await db.executescript(script)

        await db.execute(
            "INSERT INTO link(name, redirect) VALUES(?, ?)",
            ("test", "test")
        )

        await db.commit()

        r = await db.execute_fetchall("SELECT * FROM link")
        print(r)
    return "hello"




def main():
    app.run()


if __name__ == "__main__":
    main()
