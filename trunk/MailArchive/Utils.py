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
from os.path import join
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
        try: return time.strftime('%a %b %d %H:%M:%S %Z %Y', p_tuple)
        except: return ''

    def zip_file(self, id, original, data):
        path = join(CLIENT_HOME, id)
        zp = ZipFile(path, "w")
        info = ZipInfo(original)
        info.date_time =  time.localtime(time.time())[:6]
        info.compress_type = ZIP_DEFLATED
        zp.writestr(info, data)
        zp.close()
        return file(path, 'rb').read(), path

    def showSizeKb(self, p_size):
        #transform a file size in Kb
        return int(p_size/1024 + 1)

    def quote_attachment(self, name):
        return name.replace(' ', '_')