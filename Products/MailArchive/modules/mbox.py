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
import re

from mbox_email import mbox_email
from mbox_filters import mbox_filters

SPAM = 0
KEEP = 1
UNSURE = 2


def get_start_stop(msg):
    """
    the `mailbox._PartialFile` class has internal `start` & `stop`
    attributes whose name changed in newer Python versions.
    """
    partial_file = msg.fp

    if sys.version_info >= (2,6):
        start = partial_file._start
        stop = partial_file._stop

    else:
        start = partial_file.start
        stop = partial_file.stop

    return start, stop


class mbox(mbox_filters):

    def __init__(self, path):
        self.path = path
        self.size = os.path.getsize(self.path)
        self.last_modified = os.path.getmtime(self.path)
        self.cache = {}
        self.starting = None
        self.ending = None
        mbox_filters.__dict__['__init__'](self)
        self.process_mbox()

    def process_mbox(self):
        #open a MBOX file and process all its content
        self.cache = {}
        mb = mailbox.PortableUnixMailbox (open(self.path,'rb'))
        msg = mb.next()
        starting, ending = None, None
        while msg is not None:
            document = msg.fp.read()
            if document is not None:
                m = mbox_email(''.join(msg.headers))
                d = msg.getdate('Date')
                s = m.getSubject()
                (result, reason) = self.run_rules(s)
                if result:
                    if s == '': s = '(no subject)'
                    from_addr = m.getFrom()
                    f = from_addr[0]
                    if not f: f = from_addr[1]
                    index = self.get_unique_id(m)
                    start, stop = get_start_stop(msg)
                    self.cache[index] = (
                        index, start, stop-start,
                        s, d, f, m.getMessageID(), m.getInReplyTo(), m.getTo(), m.getCC()
                    )
                    #process starting, ending
                    if starting is None: starting = d
                    else:
                        if d < starting: starting = d
                    if ending is None: ending = d
                    else:
                        if d > ending: ending = d
                msg = mb.next()
        self.starting, self.ending = starting, ending
        mb = None

    def get_msg_index(self, msg): return msg[0]
    def get_msg_offset(self, msg): return msg[1]
    def get_msg_size(self, msg): return msg[2]
    def get_msg_subject(self, msg): return msg[3]
    def get_msg_date(self, msg): return msg[4]
    def get_msg_from(self, msg): return msg[5]
    def get_msg_id(self, msg): return msg[6]
    def get_msg_inreplyto(self, msg): return msg[7]
    def get_msg_to(self, msg):  return msg[8]
    def get_msg_cc(self, msg):  return msg[9]

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

    def __get_mbox_thread(self, msgs, node, depth):
        tree = []
        l = [msg for msg in msgs if msg[7] == node]
        map(msgs.remove, l)
        for msg in l:
            tree.append((depth, msg))
            tree.extend(self.__get_mbox_thread(msgs, msg[6], depth+1))
        return tree

    def get_mbox_thread(self, msgs):
        #builds threads
        r = self.__get_mbox_thread(msgs, '', 0)
        for x in msgs:
            r.append((0, x))
        return r

    def get_mbox_msgs(self):
        #returns the list of messages
        return self.cache.values()

    def count_mbox_msgs(self):
        #returns the number of messages
        return len(self.cache.keys())

    def sort_mbox_msgs(self, n, r):
        #returns a sorted list of messages
        t = [(x[n], x) for x in self.cache.values()]
        t.sort()
        if r: t.reverse()
        return [val for (key, val) in t]

    def sort_mbox_msgs_ci(self, n, r):
        #returns a sorted list of messages - sort without case-sensitivity
        t = [(x[n].lower(), x) for x in self.cache.values()]
        t.sort()
        if r: t.reverse()
        return [val for (key, val) in t]

    def get_unique_id(self, msg):
        #returns a unique id for this message based on Message-ID
        msg_id = msg.getMessageID()
        m = re.search('([\w]*)@', msg_id)
        return m.group(1) or msg.getMessageID()
        
def main():
    b = mbox(sys.argv[1])
    print b.cache
    print b.sort_mbox_msgs(3)

if __name__ == '__main__':
    main ()
