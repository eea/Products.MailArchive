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

import mailbox
import sys
import os.path

class mbox:

    def __init__(self, path):
        self.path = path
        self.size = os.path.getsize(self.path)
        self.cache = {}
        self.starting = None
        self.ending = None
        self.process_mbox()

    def process_mbox(self):
        #open a MBOX file and process all its content
        self.cache = {}
        mb = mailbox.UnixMailbox (open(self.path,'rb'))
        msg = mb.next()
        index = 1
        while msg is not None:
            document = msg.fp.read()
            if document is not None:
                d = msg.getdate('Date')
                self.cache[index] = (
                    index, msg.fp.start, msg.fp.stop-msg.fp.start,
                    msg.get('Subject'), d, msg.getaddr('From')[0],
                    msg.get('Message-ID'), msg.get('In-Reply-To')
                )
                if index == 1: self.starting = d
                self.ending = d
                index += 1
                msg = mb.next()
        mb = None

    def get_msg_index(self, msg): return msg[0]
    def get_msg_offset(self, msg): return msg[1]
    def get_msg_size(self, msg): return msg[2]
    def get_msg_subject(self, msg): return msg[3]
    def get_msg_date(self, msg): return msg[4]
    def get_msg_from(self, msg): return msg[5]
    def get_msg_id(self, msg): return msg[6]
    def get_msg_inreplyto(self, msg): return msg[7]

    def get_mbox_file(self):
        return open(self.path, 'rb').read()

    def get_mbox_msg(self, index):
        #given the message index in messages list returns the message body
        msg_body = ''
        cache_item = self.cache.get(index, None)
        if cache_item is not None:
            f = open(self.path, 'rb')
            f.seek(self.get_msg_offset(cache_item))
            msg_body = f.read(self.get_msg_size(cache_item))
            f.close()
            f = None
        return msg_body

    def get_mbox_thread(self, msgs, node=None):
        tree = []
        l = [msg for msg in msgs if msg[7] == node]
        map(msgs.remove, l)
        for msg in l:
            tree.append(msg)
            tree.extend(self.get_mbox_thread(msgs, msg[6]))
        return tree

    def get_mbox_msgs(self):
        #returns the list of messages
        return self.cache.values()

    def sort_mbox_msgs(self, n):
        #returns a sorted list of messages
        t = [(x[n], x) for x in self.cache.values()]
        t.sort()
        return [val for (key, val) in t]

def main():
    b = mbox(sys.argv[1])
    print b.cache
    print b.sort_mbox_msgs(3)

if __name__ == '__main__':
    main ()
