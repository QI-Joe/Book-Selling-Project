from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from myapp import DataBase
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time
from werkzeug.utils import secure_filename
import requests
from tempfile import NamedTemporaryFile
from flask import jsonify
from flask import send_file
import io
import re

app = Flask(__name__)
# "c60ce6a2dab928d4607837992c69a0e9e45b349b232393f0ee222ab8fdd5a512"

db = DataBase.Database_operation()
secret_key = {
    "AES_key": b"o5DJJRS8VqO7LdQlDULngL5E49AqCPbDxq5F6aFWgGmv20mU5MDBKXy6pKgkN5YiQC+NRz0anfoxUcywMnNLK03QZnZ3I60ABZ5g0m0kDlhZYTgt/hTM19th6rTheMTm",
    "salt": b">!?5u\xe7D\x02\xaf\xfa3\x01\xee]\x84`",
}


@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500


#
def save_to_ipfs(file_path):
    pinata_api_key = "c5948b18b8a7629fe5da"
    pinata_secret_api_key = db.AES_decryption(secret_key["AES_key"], secret_key["salt"])
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


#
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


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SECRET_KEY"] = "9e6c1f125a144d6a03a6bc42f926a9e6"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/back_index")
def back_index():
    return render_template("index.html")


def pw_decryption(account: str):
    res = db.get_account_info(account)
    salt_val, hashes = res[1][0][0], res[0][0][1]
    print(salt_val, hashes, "#----------------decryption", res)
    return db.AES_decryption(hashes, salt_val)


def bc_hash_decryption(bkname: str):
    res = db.get_bookname_bchash(bkname)
    salt_val, hashes = res[1][0][0], res[0][0][0]
    return db.AES_decryption(hashes, salt_val)


@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return render_template("index.html")

    username = username.lower()
    verify_user = db.get_account_info(username)
    if verify_user:
        verify_user = verify_user[0]
    if (
        verify_user
        and username == verify_user[0][0]
        and password == pw_decryption(username)
    ):
        session["username"] = username
        return redirect(url_for("home"))
    else:
        flash("Incorrect username or password. Please try again.")
        return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return render_template("signup.html")

    username = username.lower()
    if not re.match(r"\d{8}[a-z]$", username):
        flash("This is not a valid account. Please enter the student ID.")
        return render_template("signup.html")

    if not 5 < len(password) < 41:
        flash("The password must be between 6 and 40 characters.")
        return render_template("signup.html")

    verify_user = db.get_account_info(username)
    if verify_user:
        verify_user = verify_user[0]
    if verify_user and username == verify_user[0][0]:
        flash("Account already exists. Please choose a different username.")
        return render_template("signup.html")
    else:
        print(username, password, "#--------------------------------------------")
        res_pw = db.sign_up_insert(username, password)
        print(res_pw)
        # db.session.commit()
        flash("Account created successfully. Click Back to log in.")
        # return render_template("signup.html")
        return redirect(url_for("signup"))


# @app.route('/login', methods=['GET', 'POST'])  # 渲染login.html
# def login_button():
#     if request.method == 'POST':
#         # 检查用户提供的凭据是否正确
#         username = request.form['username']
#         password = request.form['password']
#         res = db.get_account_info(username)
#         if username == 'your_username' and password == 'your_password':
#             # 设置用户登录状态并重定向到 home 页面
#             session['username'] = username
#             return redirect(url_for('home'))
#         else:
#             # 如果凭据不正确，则返回登录页面并显示错误消息
#             return render_template('index.html', error='Invalid username or password')
#     else:
#         # 渲染登录页面
#         return render_template('index.html')


@app.route("/home")  # 渲染home.html
def home():
    user_name = session.get("username")
    print(db.get_account_info(user_name), "#------------------------------")
    token_number = db.get_account_info(user_name)[0][0][2]
    session["token_number"] = token_number
    owned_book = []
    for i in db.get_account_book(user_name):
        owned_book.append(i[0])
    contributed_book = []
    for i in db.get_account_shared(user_name):
        contributed_book.append(i[0])

    purchased_book = []
    for i in owned_book:
        if i not in contributed_book:
            purchased_book.append(i)
    all_user = db.get_all_user()
    all_book_shared = []
    for i in all_user:
        shared_book = db.get_account_shared(i[0])
        if not shared_book:
            continue
        all_book_shared.append(db.get_account_shared(i[0])[0][0])
    free_book = []
    for i in all_book_shared:
        if i not in owned_book:
            free_book.append(i)

    books = []
    for i in range(0, len(free_book)):
        books.append(
            {
                "title": free_book[i],
                "contributor": db.get_book_seller(free_book[i])[0][0],
                "price": db.get_price_by_book(free_book[i])[0][0],
            }
        )
    print(books)
    books_cid_add = []
    for i in range(0, len(free_book)):
        books_cid_add.append(
            {
                "title": free_book[i],
                "contributor": db.get_book_seller(free_book[i])[0][0],
                "price": db.get_price_by_book(free_book[i])[0][0],
                "bc_hash": bc_hash_decryption(free_book[i]),
            }
        )
    # books = [
    #     {'title': 'Book 1', 'contributor': 'Contributor 1', 'price': '$10'},
    #     {'title': 'Book 2', 'contributor': 'Contributor 2', 'price': '$20'},
    #     {'title': 'Book 3', 'contributor': 'Contributor 3', 'price': '$20'},
    #     # Add more books here
    # ]

    return render_template(
        "home.html",
        books=books,
        user_name=user_name,
        token_number=token_number,
        purchased_books=purchased_book,
        contributed_books=contributed_book,
    )


@app.route("/buy", methods=["GET", "POST"])
def buy():
    user_name = session.get("username")
    title = request.form.get("title")

    # cid testing-----------------------------
    print(title, user_name, "#---be remind for testing...")
    session["cid"] = bc_hash_decryption(title)
    # file_returned = download(cid)
    # print(cid, "<------------cid is here")
    # cid testing ---------------------------------

    price = float(request.form.get("price"))
    token_number = session.get("token_number")
    if token_number is None:
        return "User not logged in", 401
    if token_number < price:
        return "Not enough tokens", 400

    token_number -= price
    orders = {"account": user_name, "token": token_number}
    db.user_token_update(orders)

    target_user = db.get_book_seller(title)[0][0]
    token_for_target_user = db.get_account_info(target_user)[0][0][2]
    print(token_for_target_user, target_user, "#-----------------")
    token_for_target_user += price
    orders = {"account": target_user, "token": token_for_target_user}
    db.user_token_update(orders)
    db.user_property_insert({"account": user_name, "book": title, "buy": 1})

    session["token_number"] = token_number
    return redirect(url_for("home"))


@app.route("/logout")  # 在home.html中，点击“Logout”按钮时，会调用logout()函数，返回login.html
def logout():
    # 从 session 中删除用户信息，并重定向到 login 页面
    session.pop("username", None)
    return redirect(url_for("index"))


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
    book_title = request.args.get("book_title")
    token_price = request.args.get("token_price")
    book_hash = request.args.get("book_hash")
    # print(book_title, token_price, book_hash,'-----------------')
    # db insert book first and put it on sell shop
    orders = {
        "bookname": book_title,
        "bc_hash": book_hash,
        "account": session.get("username"),
    }
    db.books_insert(orders)
    orders_on_sell = {
        "account": session.get("username"),
        "shared_book": book_title,
        "price": token_price,
    }
    db.book_on_sell_insert(orders_on_sell)
    # 111
    return render_template(
        "receipt.html",
        book_title=book_title,
        token_price=token_price,
        book_hash=book_hash,
    )


@app.route("/download")
def download():
    cid = session.get("cid")
    print(cid, "<-----from download-------cid is here")
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
    # print("only for test: ")
    # print("now here we go: ")
