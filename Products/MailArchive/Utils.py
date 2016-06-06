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
from random import choice
from os.path import join, getmtime, isdir, isfile, getsize
from os import listdir
import urllib
from Products.PythonScripts.standard import url_quote, html_quote

from Products.PythonScripts.standard import html_quote

class Utils(object):

    def __init__(self):
        """ """
        pass

    def newlineToBr(self, p_string):
        return html_quote(p_string).replace('\n', '<br />')

    def tupleToDate(self, p_tuple):
        try: return time.strftime('%Y-%m-%d %H:%M:%S', p_tuple)
        except: return ''

    def list_difference(self, l1, l2):
        #return a list with elements from l1 that are not in l2
        return [e1 for e1 in l1 if e1 not in l2]

    def tupleToShortDate(self, p_tuple):
        try: return time.strftime('%Y-%m-%d', p_tuple)
        except: return ''

    def get_time(self):
        return time.time()

    def tupleToDateHTML(self, p_tuple):
        try: return time.strftime('%Y-%m-%dT%H:%M:%S', p_tuple)
        except: return ''

    def lines_to_list(self, value):
        """Takes a value from a textarea control and returns a list of values"""
        if type(value) == type([]):
            return value
        elif value == '':
            return []
        else:
            return filter(lambda x:x!='', value.split('\r\n'))

    def list_to_lines(self, values):
        """Takes a list of values and returns a value for a textarea control"""
        if len(values) == 0: return ''
        else: return '\r\n'.join(values)

    def replace_at(self, msg):
        return msg.replace('@', '&#64;')

    def remove_duplicates(self, l):
        d = {}
        [ d.setdefault(i,None) for i in l ]
        return d.keys()

    #We don't really care about the download of the mailboxes.
    #The mbox format is little used outside the Unix community.

    #def zip_file(self, id, original, data):
    #    path = join(CLIENT_HOME, id)
    #    zp = ZipFile(path, "w")
    #    info = ZipInfo(original)
    #    info.date_time =  time.localtime(time.time())[:6]
    #    info.compress_type = ZIP_DEFLATED
    #    zp.writestr(info, data)
    #    zp.close()
    #    return open(path, 'rb').read(), path

    def showSizeKb(self, p_size):
        #transform a file size in Kb
        return int(p_size/1024 + 1)

    def quote_attachment(self, name):
        return self.toUtf8(name).replace(' ', '_')

    def antispam(self, addr):
        """ All email adresses will be obfuscated. """
        buf = map(None, addr)
        for i in range(0, len(addr), choice((2,3,4))):
            buf[i] = '&#%d;' % ord(buf[i])
        return '<a href="mailto:%s">%s</a>' % (''.join(buf), ''.join(buf))

    def get_last_modif(self, path):
        """ Return the time of last modification of path """
        return getmtime(path)

    def get_mbox_size(self, path):
        """ return the mbox size """
        return getsize(path)

    def valid_directory(self, path):
        return isdir(path)

    def valid_file(self, path):
        return isfile(path)

    def get_files(self, path):
        if self.valid_directory(path):
            return listdir(path)
        else:
            return []

    #def delete_file(self, path):
    #    unlink(path)

    def get_mboxes(self, path, ignore_list):
        mbox = []
        others = []
        for f in self.get_files(path):
            abs_path = self.file_path(path, f)
            if f[0] == '.': # Drop 'hidden' files
                others.append((abs_path, f))
                continue
            if not self.valid_file(abs_path):    # Drop directories etc.
                continue
            if (f[:-4] in ignore_list) or (f in ignore_list):
                continue
            else:
                if open(abs_path).read(5) == 'From ':
                    mbox.append((abs_path, f))
                else:
                    others.append((abs_path, f))
        return mbox, others

    def file_path(self, path, name):
        return join(path, name)

    def xmlEncode(self, p_string):
        #encode some special chars to use in an XML string
        l_tmp = str(p_string)
        l_tmp = l_tmp.replace('&', '&amp;')
        l_tmp = l_tmp.replace('<', '&lt;')
        l_tmp = l_tmp.replace('"', '&quot;')
        l_tmp = l_tmp.replace('\'', '&apos;')
        l_tmp = l_tmp.replace('>', '&gt;')
        return l_tmp

    def urlEncode(self, s):
        #encode a string using url_encode
        return url_quote(s)

    def htmlEncode(self, s):
        #encode a string using html_quote
        return html_quote(s)

    def toUtf8(self, s):
        #convert to utf-8
        if isinstance(s, unicode): return s.encode('utf-8')
        else: return str(s)

    def toUnicode(self, s):
        #convert to unicode
        if not isinstance(s, unicode): return unicode(s, 'utf-8')
        else: return s

    def toUnicodeEx(self, s):
        #convert to unicode
        if isinstance(s, unicode): return s
        else:
            try:
                return unicode(s, 'utf-8')
            except:
                try:
                    return unicode(s, 'latin-1')
                except:
                    return s

    def urlQuote(self, value):
        #escapes single characters
        return urllib.quote(value)

    def urlUnquote(self, value):
        #transform escapes in single characters
        return urllib.unquote(value)
