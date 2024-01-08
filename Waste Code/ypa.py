# modification needed -----------------------------------------------------
def student_info_update(self, data: dict):
    update_sql, upval = "", ()
    for key, val in data.items():
        if val is None:
            print("Invalidate value, reject to update.")
            return False
    if data["table"] == "student_account":
        update_sql = """
    update `student_account` set %s=%s where `sid`=%s
    """
        upval = (self.update_standard["student_account"][data["col"]], data["val"], data["sid"])
    elif data["table"] == "admin":
        update_sql = """
        update `student_account` set %s=%s where `sid`=%s
        """
        upval = (self.update_standard["admin"][data["col"]], data["val"], data["sid"])

    if update_sql == "" or not upval:
        print("Invalid input, reject to insert.")
        return False
    try:
        self.cursor.execute(update_sql, upval)
    except Exception as e:
        print(f"Wrong Message {e}")
        return False
    return True
# -------------------------------------------------------------

# if self.sid_validation(account):
#     warnings.warn(f"SID {account} already exist, cannot register again")
#     return ["", False]

# integration of encryption and insert, after insert to decrypt the value
#     try:
#         self.cursor.execute(sql_on, value_on)
#         self.conn.commit()
#
#         self.cursor.execute(sql_user_property, val_pro)
#         self.conn.commit()
#
#         time.sleep(2)
#         print("successfully insert value.")
#     except Exception as e:
#         return [f"{e}", False]
#
#     return ["", True]