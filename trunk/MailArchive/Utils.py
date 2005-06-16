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


import time
import re

from whrandom import choice
from os.path import join, getmtime
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from StringIO import StringIO

from Products.PythonScripts.standard import url_quote, html_quote

class Utils:

    def __init__(self):
        """ """
        pass

    def newlineToBr(self, p_string):
        return html_quote(p_string).replace('\n', '<br />')

    def tupleToDate(self, p_tuple):
        try: return time.strftime('%Y-%m-%d %H:%M:%S', p_tuple)
        except: return ''

    def tupleToShortDate(self, p_tuple):
        try: return time.strftime('%Y-%m-%d', p_tuple)
        except: return ''

    def replace_at(self, msg):
        return msg.replace('@', '&#64;')

    def zip_file(self, id, original, data):
        path = join(CLIENT_HOME, id)
        zp = ZipFile(path, "w")
        info = ZipInfo(original)
        info.date_time =  time.localtime(time.time())[:6]
        info.compress_type = ZIP_DEFLATED
        zp.writestr(info, data)
        zp.close()
        return open(path, 'rb').read(), path

    def showSizeKb(self, p_size):
        #transform a file size in Kb
        return int(p_size/1024 + 1)

    def quote_attachment(self, name):
        return name.replace(' ', '_')

    def antispam(self, addr):
        """ All email adresses will be obfuscated. """
        buf = map(None, addr)
        for i in range(0, len(addr), choice((2,3,4))):
            buf[i] = '&#%d;' % ord(buf[i])
        return '<a href="mailto:%s">%s</A>' % (''.join(buf), ''.join(buf))

    def extractUrl(self, msg):
        """ Functions to identify and extract URLs"""
        #pat_url = re.compile(r'''(?x)((http|ftp|gopher)://(\w+[:.]?){2,}(/?|[^ \n\r"]+[\w/])(?=[\s\.,>)'"\]]))''')
        #return [u[0] for u in re.findall(pat_url, msg)]
        strg = re.sub(r'(?P<url>http[s]?://[-_&;,?:~=%#+/.0-9a-zA-Z]+)',
                      r'<a href="\g<url>">\g<url></a>', msg)
        return strg.strip()

    def get_last_modif(self, path):
        """ Return the time of last modification of path """
        return getmtime(path)