"""Check an email address and find the HFRC email.  Extract position or message information from the body and write it
to a database
"""


import imaplib
import os

import mysql.connector


class CheckMail:
    """Check the email inbox.  Determine msg type and pass info to DataBaseWriter class"""
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

    def execute_query(self, query):
        """Blindly execute a query"""
        cursor = self.sqlconx.cursor()
        cursor.execute(query)
        self.sqlconx.commit()
        cursor.close()

    def create_user(self, selcal_id):
        """Create a user_id for a selcal number.  Other data can be added manually later"""
        query = f"""INSERT INTO `user` (`user_id`, `selcal_number`, `f_name`, `l_name`) 
                    VALUES (NULL, {selcal_id}, NULL, NULL);"""
        self.execute_query(query)

    def base_exists(self, basename):
        """Check to see if a base exists"""
        query = f"""Select * from bases where name = '{basename}'"""
        cursor = self.sqlconx.cursor(dictionary=True, buffered=True)
        cursor.execute(query)
        if cursor.rowcount == 1:
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def create_base(self, basename):
        """Creates a base.  Other details can be added later"""
        query = f"""INSERT INTO `bases` (`base_id`, `name`, `latitude`, `longitude`) 
                VALUES (NULL, '{basename}', NULL, NULL);"""
        self.execute_query(query)

    def channel_exists(self, freq, ch_number):
        """Check to see if the channel info exists in the DB"""
        query = f"""select * 
                    from channels 
                    where frequency_khz = {freq}
                    and channel_number = {ch_number}"""
        cursor = self.sqlconx.cursor(dictionary=True, buffered=True)
        cursor.execute(query)
        cursor.close()
        if cursor.rowcount == 1:
            return True
        else:
            return False

    def create_channel(self, freq, ch_number):
        """Create a channel in the DB"""
        query = f"""INSERT INTO `channels` (`channel_id`, `frequency_khz`, `channel_number`) 
                    VALUES (NULL, '{freq}', '{ch_number}');"""
        self.execute_query(query)

    def check_base_data(self, selcal, basename, channel, frequency):
        """Convenience function to set up user and network data"""
        try:
            if not self.user_exists(selcal):
                self.create_user(selcal)
            if not self.base_exists(basename):
                self.create_base(basename)
            if not self.channel_exists(frequency, channel):
                self.create_channel(frequency, channel)
        except:
            return False
        return True

    def write_message(self, selcal, msg_timestamp, basename, message, freq, channel, ext_ref):
        """Validate params and write the message to the DB"""
        if self.check_base_data(selcal, basename, channel, freq):
            writequery = f"""insert into `messages` (`msg_id`, 
                                                     `user_id`, 
                                                     `base_id`, 
                                                     `base_timestamp`, 
                                                     `channel_id`, 
                                                     `msg`, 
                                                     `flux_reference`
                                                     )
                                VALUES (NULL,
                                        (select user_id from user where selcal_number = {selcal}),
                                        (select base_id from bases where name = '{basename}'),
                                        {msg_timestamp},
                                        (select channel_id 
                                           from channels 
                                          where frequency_khz = {freq} 
                                            and channel_number = {channel}),
                                        '{message}',
                                        '{ext_ref}'
                                        )
                        """
            self.execute_query(writequery)
        else:
            print("Could not write message due to failure to check network or user data")

    def write_position(self, selcal, msg_timestamp, basename, lat, lon, freq, channel, ext_ref):
        """Validate user and network data and then write the position data to the DB"""
        if self.check_base_data(selcal, basename, channel, freq):
            writequery = f"""INSERT INTO `positions` (`pos_id`, 
                                                      `user_id`, 
                                                      `latitude`, 
                                                      `longitude`, 
                                                      `base_id`, 
                                                      `flux_reference`, 
                                                      `channel_id`,
                                                      `msg_timestamp`) 
                             VALUES (NULL, 
                                     (select user_id from user where selcal_number = {selcal}), 
                                     {lat}, 
                                     {lon}, 
                                     (select base_id from bases where name = '{basename}'), 
                                     '{ext_ref}', 
                                     (select channel_id 
                                           from channels 
                                          where frequency_khz = {freq} 
                                            and channel_number = {channel}),
                                     {msg_timestamp});
                          """
            self.execute_query(writequery)
        else:
            print("Could not write positions due to failure while checking network or user data")


# if __name__ == "__main__":

    # CheckMail()
    # a = DatabaseWriter()
    # a.write_message(1234,
    #                 222,
    #                 'Bork',
    #                 'This is my message',
    #                 14585,
    #                 23,
    #                 'ext_referecnjce'
    #                 )
    # a.write_position(4321,
    #                  222,
    #                  'bork',
    #                  -27.1234,
    #                  153.1234,
    #                  3344,
    #                  2,
    #                  'my_ext_ref')
