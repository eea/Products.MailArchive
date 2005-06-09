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


class mbox_email:
    """ wrapper for email """

    def __init__(self, msg):
        self._msg = email.message_from_string(msg)

    def _extract_email(self, s):
        """  Extract email addresses. Thanks to Carl Scharenberg for this piece of code"""
        res = []
        mail = re.compile(r'[\w\-][\w\-\.]+@[\w\-][\w\-\.]+[a-zA-Z]{1,4}')
        res.extend(mail.findall(s))
        return res

    def getTo(self):
        buf = self._msg.get('to', None)
        if buf is None:
            return None
        return self._extract_email(buf)

    def getAuthor(self):
        buf = self.getFrom()
        e = self._extract_email(buf)[0]
        buf = buf.replace(e, '')
        return buf.replace('"', '')
    
    def getEmailFrom(self):
        buf = self.getFrom()
        return self._extract_email(buf)
        
    def getFrom(self):
        buf = self._msg.get('from', None)
        if buf is None:
            return None
        return buf

    def getSubject(self):
        return self._msg.get('subject', None)

    def getDateTime(self):
        buf = self._msg.get('date', None)
        if buf is None:
            return None
        return email.Utils.parsedate(buf)

    def getInReplyTo(self):
        return self._msg.get('In-Reply-To', None)

    def getMessageID(self):
        return self._msg.get('Message-ID', None)

    def getContent(self):
        for part in self._msg.walk():
            if part.get_content_type() in ['text/plain', 'text/html']:
                cont = part.get_payload(decode=1)
                cont.replace('<x-html>', '')
                cont.replace('</x-html>', '')
                cont.replace('<x-flowed>', '')
                cont.replace('</x-flowed>', '')
                return cont

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
