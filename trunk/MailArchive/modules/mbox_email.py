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


import email
import re
from os.path import join
from email.Utils import parseaddr, parsedate, getaddresses
from email.Header import decode_header

charset_table = {
     "window-1252": "cp1252",
     "windows-1252": "cp1252",
     "nil": "Latin-1",
     "default_charset": "Latin-1",
     "x-unknown": "Latin-1",
}

def to_entities(str):
    res = []
    for ch in str:
        och = ord(ch)
        if och > 127:
            res.append('&#%d;' % och)
        elif och == 38:
            res.append('&amp;')
        elif och == 60:
            res.append("&lt;")
        elif och == 62:
            res.append("&gt;")
        else:
            res.append(ch)
    return ''.join(res)

class mbox_email:
    """ wrapper for email """

    def __init__(self, msg):
        self._msg = email.message_from_string(msg)

    def getTo(self):
        res = []
        buf = getaddresses(self._msg.get_all('to', ''))
        for i in buf:
            data, enc = decode_header(i[0])[0]
            if enc is not None:
                charset  = charset_table.get(enc, enc)
                data = unicode(data, charset).encode('utf-8')
            res.append((data, i[1]))
        return res
            
    def getFrom(self):
        buf = parseaddr(self._msg.get('from', ''))
        data, enc = decode_header(buf[0])[0]
        if enc is not None:
            charset  = charset_table.get(enc, enc)    
            return (unicode(data, charset).encode('utf-8'), buf[1])
        return buf

    def getCC(self):
        res = []
        buf = getaddresses(self._msg.get_all('cc', ''))
        for i in buf:
            data, enc = decode_header(i[0])[0]
            if enc is not None:
                charset  = charset_table.get(enc, enc)
                data = unicode(data, charset).encode('utf-8')
            res.append((data, i[1]))
        return res

    def getSubject(self):
        buf = self._msg.get('subject', '')
        data, enc = decode_header(buf)[0]
        if enc is not None:
            charset  = charset_table.get(enc, enc)    
            return unicode(data, charset).encode('utf-8')
        return buf

    def getDateTime(self):
        return parsedate(self._msg.get('date', None))

    def getInReplyTo(self):
        return self._msg.get('In-Reply-To', '')

    def getMessageID(self):
        return self._msg.get('Message-ID', '')

    def getContent(self):
        payloads = []
        for part in self._msg.walk():
            ct_type = part.get_content_type()
            if ct_type in ['text/plain', 'text/html']:
                p = part.get_payload(decode=1)
                charset = self._msg.get_param("charset")
                if charset is None:
                    charset = "Latin-1"
                charset = charset.lower()
                charset = charset_table.get(charset, charset)
                p = unicode(p, charset)
                p = to_entities(p)
                payloads.append(p.encode('ascii'))
                return "".join(payloads)

    def getAttachments(self):
        atts = []
        for part in self._msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            filename = part.get_filename()
            if filename:
                atts.append(filename)
            #if not filename:
            #    ext = mimetypes.guess_extension(part.get_type())
            #    if not ext:
            #        # Use a generic bag-of-bits extension
            #        ext = '.bin'
            #        filename = 'unknown%03d%s' % (counter, ext)
            #counter += 1
        return atts
    
    def getAttachment(self, filename):
        for part in self._msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if filename == part.get_filename():
                return part.get_payload(decode=1)
        return None
