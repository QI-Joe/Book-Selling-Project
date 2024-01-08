import hashlib
import time
import uuid
import warnings

import pymysql
from Crypto.Cipher import AES
from Crypto import Random
import base64


class Link_Database:
    __variables: dict = {
        "host": "rm-3nspho22o594ka0w4ko.mysql.rds.aliyuncs.com",
        "account": "comp3334_g11",
        "password": "Comp3334",
        "db_name": "comp3334",
        "port": 3306,
        "charset": "utf8",
    }

    __salt: dict = {
        "db_name": "salt",
        "account": "qishihao01",
        "password": "20011214Db#",
    }
    _saltconn = None
    _saltcursor = None

    def __init__(self) -> None:
        retryCount, initCount = 10, 0
        while initCount < retryCount:
            try:
                self.conn = pymysql.connect(
                    host=self.__variables["host"],
                    user=self.__variables["account"],
                    password=self.__variables["password"],
                    db=self.__variables["db_name"],
                    port=self.__variables["port"],
                    charset=self.__variables["charset"],
                )
                print("Successful link with database.")
                self.cursor = self.conn.cursor()
                break
            except Exception as e:
                print(f"Cannot link with database, error message {e}.")
                initCount += 1

        if initCount > 9:
            exit(0)

        return

    def _salt_conn(self):
        retryCount, initCount = 10, 0
        while initCount < retryCount:
            try:
                self._saltconn = pymysql.connect(
                    host=self.__variables["host"],
                    user=self.__salt["account"],
                    password=self.__salt["password"],
                    db=self.__salt["db_name"],
                    port=self.__variables["port"],
                    charset=self.__variables["charset"],
                )
                print("Successful link with salt database.")
                self._saltcursor = self._saltconn.cursor()
                break
            except Exception as e:
                print(f"Cannot link with salt database, error message {e}.")
                initCount += 1

        if initCount > 9:
            exit(0)
        return

    def re_define_parameter(self, variable: dict) -> bool:
        if not variable:
            return False
        for key, val in variable.items():
            if key in self.__variables.keys() and val is not None:
                self.__variables[key] = val
            else:
                print(f"Wrong parameter input, key {key}, val {val}")
        return True

    def return_cursor(self):
        return self.cursor


class Database_operation(Link_Database):
    cursor: pymysql.connect.cursor
    bs = AES.block_size

    update_standard: dict = {
        "student_account": {"pw": "`password`", "hashes": "`hashes`", "name": "`name`"},
        "admin": {"pw": "`password`"},
    }

    def __init__(self):
        super().__init__()
        self.cursor = self.return_cursor()
        self._salt_conn()

    # when you know the account , you can gain the pw, name and its token
    def get_account_info(self, account):
        sql = """SELECT * FROM `user`
        WHERE account = %s;"""
        sql_salt = """select salt from `salt_hash` where account=%s"""

        try:
            self.cursor.execute(sql, (account,))
            results = self.cursor.fetchall()
            self._saltcursor.execute(sql_salt, (account,))
            results1 = self._saltcursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False

        return (results, results1)

    def get_all_user(self):
        sql = """select account from `user`;"""
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False
        return results

    def get_price_by_book(self, bkname: str):
        sql, val = """select `price` from `book_on_sell` where `shared_book`=%s;""", (
            bkname,
        )
        try:
            self.cursor.execute(sql, val)
            results = self.cursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False
        return results

    # when you know the account, you can gain owned book name and its brought situation.
    def get_account_book(self, account):
        sql = """SELECT owned_book, brought FROM `user_property`
        WHERE account = %s;"""
        try:
            self.cursor.execute(sql, (account,))
            results = self.cursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False

        return results

    # when you know the account, know the shared book name and its price.
    def get_account_shared(self, account):
        sql = """SELECT shared_book, price FROM `book_on_sell`
        WHERE account = %s;"""
        try:
            self.cursor.execute(sql, (account,))
            results = self.cursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False

        return results

    # when you know the book name, get the bc hash
    def get_bookname_bchash(self, bookname: str):
        (
            sql,
            values,
        ) = """SELECT bc_hash FROM `books`
        WHERE book_name = %s;""", (
            bookname,
        )
        sql_salt = """select salt from `bc_hash` where book_name=%s;"""
        try:
            self.cursor.execute(sql, bookname)
            results = self.cursor.fetchall()
            self._saltcursor.execute(sql_salt, values)
            result_salt = self._saltcursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False

        return (results, result_salt)

    def get_book_seller(self, bookname: str):
        sql, val = "select account from `book_on_sell` where `shared_book`=%s;", (
            bookname,
        )
        try:
            self.cursor.execute(sql, val)
            res = self.cursor.fetchall()
        except Exception as e:
            return [f"exception message is {e}", False]
        return res

    def get_all_book(self):
        sql = "select `book_name` from `books`"
        try:
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
        except Exception as e:
            return [f"exception message is {e}", False]
        return res

    def get_salt(self, account):
        sql = """select salt from `salt_hash` where account=%s;"""
        try:
            self._saltcursor.execute(sql, account)
            results = self._saltcursor.fetchall()
        except Exception as e:
            print(f"Exception message is {e}")
            return False

        return results

    def salt_encode(self, salt: bytes):
        return salt.decode("iso-8859-1")

    def salt_decode(self, enc_salt: str):
        return enc_salt.encode("iso-8859-1")

    def salt_generate(self):
        return uuid.uuid4().bytes

    def encrpyion_passowrd(self, pw: str, salt: bytes):
        pwencode = pw.encode("utf-8")
        xored = bytearray()
        for times in range(len(salt)):
            xored.append(salt[times] ^ pwencode[times % len(salt)])
        return hashlib.sha256(xored).hexdigest()

    # https://stackoverflow.com/questions/12524994/encrypt-and-decrypt-using-pycrypto-aes-256
    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def AES_encryption(self, pw: str, salt):
        pw = self._pad(pw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(salt, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(pw.encode()))

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]

    def AES_decryption(self, enc, salt):
        dec = base64.b64decode(enc)
        iv = dec[: AES.block_size]
        cipher = AES.new(salt, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(dec[AES.block_size :])).decode("utf-8")

    def pw_encode(self, pw: str):
        salt = self.salt_generate()
        return self.AES_encryption(pw, salt), salt

    def sid_validation(self, sid: str):
        return self.get_account_book(sid)

    def data_validation(self, data: dict) -> bool:
        for key, val in data.items():
            if not val:
                return False
        return True

    def execute_commit(self, cursors: dict):
        for key, val in cursors.items():
            cursor, conn = None, None
            if key[0:6] == "normal":
                cursor, conn = self.cursor, self.conn
            elif key[0:4] == "salt":
                cursor, conn = self._saltcursor, self._saltconn
            else:
                return ["invalidate order, reject to execute", False]
            try:
                cursor.execute(val[0], val[1])
                conn.commit()
                time.sleep(2)
            except Exception as e:
                return [f"{e}", False]

        return ["successfully injected", True]

    def sign_up_insert(self, account: str, password: str, token: int = 50) -> list:
        # validation needed
        if not password or not account:
            return []
        pw_encoded, salt = self.pw_encode(password)
        (
            sql_pw,
            val_pw,
        ) = """INSERT INTO `user` (`account`, `pw`, `token`) values (%s, %s, %s);""", (
            account,
            pw_encoded,
            int(token),
        )
        (
            sql_salt,
            val_salt,
        ) = "INSERT INTO `salt_hash` (`account`, `salt`) values (%s, %s);", (
            account,
            salt,
        )

        orders = {"normal": (sql_pw, val_pw), "salt": (sql_salt, val_salt)}
        return self.execute_commit(orders)

    def books_insert(self, data: dict):
        """
        when user plan to share and sold a book
        :param data: contains book name, account, bc_hash. book_name is supposed no longer than 50 words
        :return:
        """
        data["bc_hash"], hash_salt = self.pw_encode(data["bc_hash"])
        (
            sql_on,
            value_on,
        ) = """insert into `books` (`book_name`, `bc_hash`) values (%s, %s);""", (
            data["bookname"],
            data["bc_hash"],
        )
        (
            sql_salt,
            value_salt,
        ) = """insert into `bc_hash`(`book_name`, `salt`) values (%s, %s);""", (
            data["bookname"],
            hash_salt,
        )
        sql_user_property, val_pro = (
            """insert into `user_property` (`account`, `owned_book`, `brought`) values (%s, %s, %s)""",
            (data["account"], data["bookname"], False),
        )

        orders = {
            "normal": (sql_on, value_on),
            "normal1": (sql_user_property, val_pro),
            "salt": (sql_salt, value_salt),
        }
        return self.execute_commit(orders)

    def book_on_sell_insert(self, data):
        """
        plan to implement verification and validation in another class.
        :param data:
        :return:
        """
        (
            sql_booksell,
            val,
        ) = """insert into `book_on_sell` (`account`, `shared_book`, `price`)
                        values (%s, %s, %s)""", (
            data["account"],
            data["shared_book"],
            data["price"],
        )

        orders = {"normal": (sql_booksell, val)}
        return self.execute_commit(orders)

    def user_property_insert(self, data: dict):
        """
        used to update table user_property when user buy a book
        :param data:
        """
        (
            sql,
            value,
        ) = """insert into `user_property` (`account`, `owned_book`, `brought`)
                    values (%s, %s, %s);""", (
            data["account"],
            data["book"],
            data["buy"],
        )
        orders = {"normal": (sql, value)}
        return self.execute_commit(orders)

    def user_token_update(self, data):
        """
        update user token after buying a book.
        :param data:
        """
        (
            sql,
            value,
        ) = """update `user` 
        set `user`.`token`=%s where `user`.`account`=%s;""", (
            data["token"],
            data["account"],
        )

        orders = {"normal": (sql, value)}
        return self.execute_commit(orders)


def insert_test():
    db = Database_operation()
    data_book_insert = {"account": "guhoipjo", "bookname": "C++ advanced skills", "bc_hash": "0xQmZMJJpqhNHJcpdUSBEGASsUmAZdCfabMnBFebQZLVHtws"}
    db.books_insert(data_book_insert)
    data = {"account": "guhoipjo", "shared_book": "C++ advanced skills", "price": 8}
    db.book_on_sell_insert(data)
    # db.user_token_update({"token": 40, "account": "2004478D"})
    # db.user_property_insert({"book": "my craft", "account": "2004478D", "buy": True})


# def test_encryption():
#     db = Database_operation()
#     res = db.get_bookname_bchash("blockchain_new")
#     salt_val, hashes = res[1][0][0], res[0][0][0]
#     db.AES_decryption(hashes, salt_val)


if __name__ == "__main__":
    secret_key="c60ce6a2dab928d4607837992c69a0e9e45b349b232393f0ee222ab8fdd5a512"
    db = Database_operation()
    # salt=db.salt_generate()
    # ensk=db.AES_encryption(secret_key, salt=salt)
    # print(salt, "\n", ensk)
    salt, ensk=b">!?5u\xe7D\x02\xaf\xfa3\x01\xee]\x84`",\
               b"o5DJJRS8VqO7LdQlDULngL5E49AqCPbDxq5F6aFWgGmv20mU5MDBKXy6pKgkN5YiQC+NRz0anfoxUcywMnNLK03QZnZ3I60ABZ5g0m0kDlhZYTgt/hTM19th6rTheMTm"
    print(db.AES_decryption(ensk, salt)==secret_key)