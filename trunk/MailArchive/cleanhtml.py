#!/usr/bin/python
# -*- coding: utf-8 -*-
# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Original Code is MailArchive version 1.0.
#
# The Initial Developer of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Contributor(s):
# Soren Roug, EEA
#
#
#
# $Id: cleanhtml.py 2783 2004-12-08 16:40:38Z roug $
#
import string
import htmlentitydefs
from sgmllib import SGMLParser
from types import StringType

# Elements we don't like
bad_elements = ( 'script', 'style','object','applet','embed','iframe','layer' )

good_elements = ( 'p','b','font','i','em','strong','pre','span','div','li','ol','ul','dl',
 'dd','dt','table','thead','tbody','tr','th','td')

closed_elements = ( 'br','hr','img','colspec')

good_attributes = ('alt', 'href', 'title', 'src', 'class', 'style', 'name', 'id',
'cellspacing', 'cellpadding', 'width', 'border','bgcolor','color','align','valign','face','size',
'height','colspan','rowspan' )

bad_attributes = ('target',)

class HTMLCleaner(SGMLParser):
    """ This class cleans malicous HTML code
        You call it like this:

        mycleaner = HTMLCleaner('iso8859-1')
        print mycleaner.clean(data)

    """

    def __init__(self, encoding='iso8859-1'):
        SGMLParser.__init__(self)
        self.encoding = encoding
        self.tagstack = []
        self.checkflag = 0  # Are we in a tag we check?
        self.__data = []

    def clean(self, data, encoding='iso8859-1'):
        """ Spellcheck a word """
        self.encoding = encoding
        self.tagstack = []
        self.checkflag = 0  # Are we in a tag we check?
        self.__data = []
        self.feed(data)
        return string.join(self.__data,'')


    def handle_data(self, data):
        if self.checkflag == 1:
            if type(data) == StringType:
                data = unicode(data, self.encoding)
            self.__data.append(data)

    def unknown_starttag(self, tag, attrs):
        self.tagstack.append(tag)
        if tag in bad_elements:
            self.checkflag = 0
        elif tag == 'body':
            self.checkflag = 1
            self.__data.append('<div class="msgbody">')
        elif self.checkflag == 1:
            self.__data.append("<" + tag)
            for attr in attrs:
                if attr[0] in good_attributes:
                    self.__data.append(' %s="%s"' % ( attr[0], attr[1]))
            if tag in closed_elements:
                self.__data.append(" />")
            else:
                self.__data.append(">")

    def unknown_endtag(self, tag):
        self.tagstack.pop()
        if tag in bad_elements:
            self.checkflag = 1
        elif tag == 'body':
            self.checkflag = 0
            self.__data.append('</div>')
        elif tag in closed_elements:
            pass
        elif self.checkflag == 1:
            self.__data.append("</%s>" % tag)

    def handle_charref(self, name):
        """Handle character reference for UNICODE"""
        try:
            n = int(name)
        except ValueError:
            self.unknown_charref(name)
            return
        if not 0 <= n <= 65535:
            self.unknown_charref(name)
            return
        self.handle_data(unichr(n))

    def handle_entityref(self, name):
        """Handle entity references.
        """
        table = htmlentitydefs.name2codepoint
        if name in table:
            self.handle_data(unichr(table[name]))
        else:
            self.unknown_entityref(name)
            return

conn = open('testdata')
if not conn:
    raise IOError, "Failure in open"
data = conn.read()
conn.close()

mycleaner = HTMLCleaner('iso8859-1')
print mycleaner.clean(data)


