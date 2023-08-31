from quart import Quart

app = Quart(__name__)


@app.route("/")
async def home():
    return "Hello"


def main():
    app.run()


if __name__ == "__main__":
    main()
