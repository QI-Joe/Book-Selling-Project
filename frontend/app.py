from flask import Flask, request
import json

app = Flask(__name__)


@app.route("/download", methods=["GET", "POST"])
def download():
    print("---------------------\n", request)
    return json.dumps({})


if __name__ == "__main__":
    app.run(debug=True)
