"""Check an email address and find the HFRC email.  Extract position or message information from the body and write it
to a database
"""


import imaplib
import os


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


if __name__ == "__main__":
    CheckMail()
