"""Check an email address and find the HFRC email.  Extract position or message information from the body and write it
to a database
"""

import configparser
import imaplib
import os


class CheckMail:
    def __init__(self):
        os.chdir('../')
        config = configparser.ConfigParser()
        config.read('configs/config')
        # noinspection PyTypeChecker
        self.mail = imaplib.IMAP4_SSL(host=config['email']['imap'],
                                      port=config['email']['port']
                                      )
        self.mail.login(config['email']['username'],
                        config['email']['password']
                        )
        self.mail.select(readonly=True)
        print(self.mail.search(None, 'ALL'))


if __name__ == "__main__":
    CheckMail()
