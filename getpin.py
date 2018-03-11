#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      danal
#
# Created:     09/03/2018
# Copyright:   (c) danal 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import time
from itertools import chain
import email
import imaplib
import re
import sys

imap_ssl_hosts = {
    'yahoo': {'url': 'imap.mail.yahoo.com', 'port': 993},
    'gmail': {'url': 'imap.mail.yahoo.com', 'port': 993},
    'mail':  {'url': 'imap.mail.com', 'port': 993}
    }


class PinRetriever:
    def __init__(self, username, password, timeout = 120):
        self.username = username
        self.password = password
        self.timeout  = timeout
        if "@gmail" in self.username:
            self.provider = "gmail"
        elif "@yahoo" in self.username:
            self.provider = "yahoo"
        elif "@mail" in self.username:
            self.provider = "mail"
        else:
            return False

    def search_string(self, uid_max, criteria):
        c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
        return '(%s)' % ' '.join(chain(*c))

    def get_pin_code(self, sender, max_age=20):
        criteria = {'FROM': sender}
        start_time = time.time()
        last_mail = 0
        while time.time() - start_time < self.timeout:
            server = imaplib.IMAP4_SSL(imap_ssl_hosts[self.provider]["url"], imap_ssl_hosts[self.provider]["port"])
            server.login(self.username, self.password)
            server.select('INBOX')

            result, data = server.uid('search', None, self.search_string(last_mail, criteria))
            uids = [int(s) for s in data[0].split()]
            if uids:
                if last_mail < max(uids):
                    last_mail = max(uids)
                    result, data = server.uid('fetch', str(last_mail), '(RFC822)')  # fetch entire message
                    msg = email.message_from_bytes(data[0][1])
                    if ((time.time() - email.utils.mktime_tz(email.utils.parsedate_tz(msg['Date']))) < max_age):
                        pin = re.findall(">([0-9]{6})<", str(data[0][1]))
                        if pin != []:
                            print(pin[0])
                            server.logout()
                            return pin[0]
            time.sleep(5)
        server.logout()
        print("NONE")
        return None

def main(**args):
    if "email" in args.keys() and "password" in args.keys() and "sender" in args.keys():
        if "timeout" in args.keys():
            pinRetriever = PinRetriever(args["email"], args["password"], int(args["timeout"]))
        else:
            pinRetriever = PinRetriever(args["email"], args["password"])
        return pinRetriever.get_pin_code(args["sender"], 20)
    else:
        return False

if __name__ == '__main__':
    main(**dict(arg.split('=') for arg in sys.argv[1:]))


