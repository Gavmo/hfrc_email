"""Check an email address and find the HFRC email.  Extract position or message information from the body and write it
to a database
"""


import imaplib
import os

import mysql.connector


class CheckMail:
    def __init__(self):
        os.chdir('../')
        # noinspection PyTypeChecker
        self.mail = imaplib.IMAP4_SSL(host=os.environ.get('IMAPSERVER'),
                                      port=os.environ.get('IMAPPORT')
                                      )
        self.mail.login(os.environ.get('IMAPUSERNAME'),
                        os.environ.get('IMAPSECRET')
                        )
        self.mail.select(readonly=True)
        print(self.mail.search(None, 'ALL'))


class DatabaseWriter:
    def __init__(self):
        try:
            self.sqlconx = mysql.connector.connect(user='root',
                                                   password=os.environ.get('MYSQL_ROOT_PASSWORD'),
                                                   host='172.16.51.171',
                                                   port=32769,
                                                   database='hfrc_data',
                                                   raise_on_warnings=False
                                                   )
        except TimeoutError as e:
            print(e)

    def user_exists(self, selcal_id):
        """Check the DB for the presence of the selcal_id in the user table"""
        query = rf"""Select * from user where selcal_number = {selcal_id}"""
        cursor = self.sqlconx.cursor(dictionary=True, buffered=True)
        cursor.execute(query)
        if cursor.rowcount == 1:
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def create_user(self, selcal_id):
        """Create a user_id for a selcal number.  Other data can be added manually later"""
        query = f"""INSERT INTO `user` (`user_id`, `selcal_number`, `f_name`, `l_name`) 
                    VALUES (NULL, {selcal_id}, NULL, NULL);"""
        print(query)
        cursor = self.sqlconx.cursor()
        cursor.execute(query)
        self.sqlconx.commit()
        cursor.close()



if __name__ == "__main__":
    # CheckMail()
    a = DatabaseWriter()
    print(a.user_exists(1616))
    if not a.user_exists(1616):
        a.create_user(1616)
    print(a.user_exists(1616))

