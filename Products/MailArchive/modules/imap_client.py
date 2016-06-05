#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is MailArchive 0.5
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania are
#Copyright (C) 2000 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: 
#    Cornel Nitu (Finsiel Romania)
#    Dragos Chirila (Finsiel Romania)

import imaplib
import re
import email

MAILBOXES_PATTERN = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

class imap_client(object):

    def __init__(self, servername, username, password):
        """ """
        self.__imap_servername = servername
        self.__imap_username = username
        self.__imap_password = password
        self.__imap_connection = None
        self.__imap_flg = False

    def connOpen(self):
        #open connection and login
        try:
            self.__imap_connection = imaplib.IMAP4_SSL(self.__imap_servername)
            rv, data = self.__imap_connection.login(self.__imap_username, self.__imap_password)
            if rv=='OK':
                self.__imap_flg = True
        except Exception, error:
            pass

    def connValid(self):
        #check if the connection is valid
        return self.__imap_connection is not None and self.__imap_flg

    def connClose(self):
        #logout and close connection
        try: self.__imap_connection.logout()
        except: pass
        self.__imap_connection = None
        self.__imap_flg = False

    def listMailboxes(self, ignore_list):
        r = []
        if self.connValid():
            rv, data = self.__imap_connection.list()
            if rv=='OK':
                for item in data:
                    flags, delimiter, mailbox_name = MAILBOXES_PATTERN.match(item).groups()
                    mailbox_name = mailbox_name.strip('"')
                    if mailbox_name not in ignore_list:
                        r.append(mailbox_name)
        return r

    def listMailboxesEx(self, ignore_list):
        r = []
        if self.connValid():
            rv, data = self.__imap_connection.list()
            if rv=='OK':
                for item in data:
                    flags, delimiter, mailbox_name = MAILBOXES_PATTERN.match(item).groups()
                    mailbox_name = mailbox_name.strip('"')
                    if mailbox_name not in ignore_list:
                        mailbox_counter = self.selectMailbox(mailbox_name)
                        r.append({'name': mailbox_name, 'counter': mailbox_counter})
        return r

    def selectMailbox(self, mailbox_name):
        #select the mailbox and returns the count of messages in mailbox
        r = 0
        if self.connValid():
            rv, data = self.__imap_connection.select(mailbox_name, readonly=True)
            if rv == 'OK':
                r = int(data[0])
        return r

    def getMailboxMessages(self, mailbox_name):
        #get all messages in the mailbox
        r = []
        mailbox_counter = self.selectMailbox(mailbox_name)
        if mailbox_counter>0:
            rv, messages = self.__imap_connection.search(None, 'ALL')
            if rv == 'OK':
                for num in messages[0].split():
                    rv, msg = self.__imap_connection.fetch(num, '(RFC822.HEADER)')
                    if rv != 'OK':
                        #ERROR getting message: skip it
                        continue
                    r.append(email.message_from_string(msg[0][1]))
        return r

    def getMailBoxMessageBody(self, mailbox_name, msg_id):
        #get a message by Message-ID
        r = ''
        mailbox_counter = self.selectMailbox(mailbox_name)
        if mailbox_counter>0:
            rv, messages = self.__imap_connection.search(None, '(HEADER Message-ID "%s")' % msg_id)
            if rv == 'OK':
                num = messages[0].split()[0]
                rv, msg = self.__imap_connection.fetch(num, '(RFC822)')
                if rv == 'OK':
                    r = msg[0][1]
        return r
