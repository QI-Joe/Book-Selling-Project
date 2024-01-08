from flask import Flask, render_template, redirect, url_for, request, session
from flask_wtf import FlaskForm
from wtforms import StringField
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
import requests
from tempfile import NamedTemporaryFile
from flask import jsonify
import os
import tempfile
from flask import send_file
import io

app = Flask(__name__)


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


import requests


def save_to_ipfs(file_path):
    pinata_api_key = "c5948b18b8a7629fe5da"
    pinata_secret_api_key = (
        "c60ce6a2dab928d4607837992c69a0e9e45b349b232393f0ee222ab8fdd5a512"
    )
    # Update the following path with the correct path to your CA certificates file
    cert_path = "root_certificates.pem"
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_api_key,
    }

    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, headers=headers, files=files, verify=cert_path)

    app.logger.info("Response: %s", response.text)

    if response.status_code == 200:
        result = response.json()
        file_cid = result["IpfsHash"]
    else:
        raise Exception("Error uploading to Pinata: {}".format(response.text))

    return file_cid


@app.route("/upload_to_pinata", methods=["POST"])
def upload_to_pinata():
    file = request.files["file"]
    filename = secure_filename(file.filename)

    # 将文件保存到临时文件夹
    with NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    # 保存文件到 IPFS 并获取 CID
    file_cid = save_to_ipfs(temp_file_path)
    return {"file_cid": file_cid}


@app.route("/login", methods=["GET", "POST"])  # 渲染login.html
def login():
    if request.method == "POST":
        # 检查用户提供的凭据是否正确
        username = request.form["username"]
        password = request.form["password"]
        if username == "your_username" and password == "your_password":
            # 设置用户登录状态并重定向到 home 页面
            session["username"] = username
            return redirect(url_for("home"))
        else:
            # 如果凭据不正确，则返回登录页面并显示错误消息
            return render_template("login.html", error="Invalid username or password")
    else:
        # 渲染登录页面
        return render_template("login.html")


@app.route("/")  # 渲染home.html
def home():
    # 从 books.txt 文件中读取书籍列表
    with open("Textbook System/books.txt", "r") as f:
        books_data = f.readlines()

    # 解析书籍数据，并将其转换为字典列表
    books = []
    for book_data in books_data:
        title, contributor, price, cid = book_data.strip().split(",")
        books.append(
            {"title": title, "contributor": contributor, "price": price, "cid": cid}
        )

    account_id = "12345"
    user_name = "John Doe"
    token_number = "ABCDE12345"
    purchased_books = ["Book 1", "Book 2"]
    contributed_books = ["Book 3", "Book 4"]

    return render_template(
        "home.html",
        books=books,
        account_id=account_id,
        user_name=user_name,
        token_number=token_number,
        purchased_books=purchased_books,
        contributed_books=contributed_books,
    )


@app.route("/logout")  # 在home.html中，点击“Logout”按钮时，会调用logout()函数，返回login.html
def logout():
    # 从 session 中删除用户信息，并重定向到 login 页面
    session.pop("username", None)
    return redirect(url_for("login"))


# 在home.html中，点击“Make a Contribution”按钮时，会调用make_contribute()函数，进入contribute.html
# @app.route('/make_contribute')
# def make_contribute():
#     return redirect(url_for('contribute'))


class UploadForm(FlaskForm):
    book_title = StringField("Book Title")
    token_price = StringField("Token Price")
    file = FileField("Upload", validators=[FileAllowed(["pdf", "txt", "doc"])])


@app.route("/contribute", methods=["GET", "POST"])  # 渲染contribute.html
def contribute():
    return render_template("contribute.html")


@app.route("/submit", methods=["POST"])
def submit():
    book_title = request.form["bookTitle"]
    token_price = request.form["tokenPrice"]
    file = request.files["fileInput"]
    filename = secure_filename(file.filename)

    # 将文件保存到临时文件夹
    with NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    # 保存文件到IPFS并获取CID
    book_hash = save_to_ipfs(temp_file_path)

    return redirect(
        url_for(
            "receipt",
            book_title=book_title,
            token_price=token_price,
            book_hash=book_hash,
        )
    )


@app.route("/receipt")
def receipt():
    book_title = request.args.get("bookTitle")
    token_price = request.args.get("tokenPrice")
    book_hash = request.args.get("fileHash")
    return render_template(
        "receipt.html",
        book_title=book_title,
        token_price=token_price,
        book_hash=book_hash,
    )


@app.route("/download", methods=["GET"])
def download():
    cid = request.args.get("cid", None)

    if not cid:
        return jsonify({"error": "Missing CID parameter"}), 400

    ipfs_gateway_url = "https://ipfs.io/ipfs/"
    file_url = ipfs_gateway_url + cid

    response = requests.get(file_url, stream=True)

    if response.status_code == 200:
        """
        content_type = response.headers.get('Content-Type')
        if content_type != 'application/pdf':
            return jsonify({"error": "The file downloaded is not a PDF"}), 400
        """
        file_data = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            file_data.write(chunk)

        file_data.seek(0)

        # You can use any filename or derive it from the content if available
        # Make sure to sanitize the filename
        file_name = "downloaded_file"

        return send_file(
            file_data,
            as_attachment=True,
            download_name=file_name,
            mimetype="application/pdf",
        )
    else:
        return jsonify({"error": "Error downloading file from IPFS"}), 500


if __name__ == "__main__":
    app.run(debug=True)
