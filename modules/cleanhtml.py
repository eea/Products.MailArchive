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
from HTMLParser import HTMLParser
from types import StringType

# Elements we don't like
bad_elements = (
    'script', 'style','object','applet','embed', 'frame', 'iframe','layer',
    'param', 'x-html', 'x-flowed'
)

# Unused
good_elements = (
    'p','b','font','i','em','strong','pre','span','div','li','ol','ul','dl',
    'dd','dt','table','thead','tbody','tr','th','td'
)

empty_elements = ( 'area', 'br', 'col', 'hr','img', 'input', 'isindex'
)

good_attributes = (
    'abbr', 'accept-charset', 'accept', 'accesskey', 'action', 'align',
    'alink', 'alt', 'axis', 'bgcolor', 'border', 'cellpadding', 'cellspacing',
    'char', 'charoff', 'charset', 'checked', 'cite', 'class', 'clear',
    'color', 'cols', 'colspan', 'compact', 'coords', 'dir', 'disabled',
    'enctype', 'face', 'for', 'frame', 'frameborder', 'headers', 'height',
    'hreflang', 'hspace', 'id', 'ismap', 'label', 'lang', 'maxlength',
    'method', 'multiple', 'name', 'nohref', 'noshade', 'nowrap', ' readonly',
    'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape',
    'size', 'src', 'start', 'style', 'summary', 'target', 'title', 'type',
    'valign', 'value', 'width'
)

bad_attributes = ('target',)

class HTMLCleaner(HTMLParser):
    """ This class cleans malicous HTML code
        You call it like this:

        mycleaner = HTMLCleaner('iso8859-1')
        print mycleaner.clean(data)

    """

    def __init__(self, encoding='iso8859-1'):
        HTMLParser.__init__(self)
        self.encoding = encoding
        self.tagstack = []
        self.checkflag = 0  # Are we in a tag we check?
        self.inbody = 0
        self.__data = []

    def clean(self, data, encoding='iso8859-1'):
        """ Spellcheck a word """
        self.encoding = encoding
        self.tagstack = []
        self.checkflag = 0  # Are we in a tag we check?
        self.inbody = 0
        self.__data = []
        self.feed(data)
        return string.join(self.__data,'')


    def handle_data(self, data):
        if self.checkflag == 1:
            if type(data) == StringType:
                data = unicode(data, self.encoding)
            self.__data.append(data)

#   def start_br(self, attrs):
#       self.__data.append("<br")
#       self.__data.append(" />")

#   def end_br(self):
#       self.__data.append("END")

    def handle_starttag(self, tag, attrs):
        if tag in ('p','td','tr'): # This tag cannot nest - so close it
            self.handle_endtag(tag)
        self.tagstack.insert(0, tag)
        if tag in bad_elements and self.inbody == 1:
            self.checkflag = 0
        elif tag == 'body':
            self.checkflag = 1
            self.inbody = 1
            self.__data.append('<div class="msgbody">')
        elif self.checkflag == 1:
            self.__data.append("<" + tag)
            for attr in attrs:
                if attr[0] == 'src':
                    self.__data.append(' %s="reference-removed"' %  attr[0])
                elif attr[0] == 'href':
		    # Don't allow content spam
                    self.__data.append(' %s="%s" rel="nofollow"' % ( attr[0], attr[1]))
                elif attr[0] in good_attributes:
                    self.__data.append(' %s="%s"' % ( attr[0], attr[1]))
            if tag in empty_elements:
                self.__data.append(" />")
            else:
                self.__data.append(">")

    def handle_endtag(self, tag):
        if len(self.tagstack) == 0:
            return # Too many pops
        if tag not in self.tagstack:
            return # Tag was not opened
        i = self.tagstack.index(tag)
        for tag in self.tagstack[:i+1]:
            if tag in bad_elements and self.inbody == 1:
                self.checkflag = 1
            elif tag == 'body':
                self.checkflag = 0
                self.__data.append('</div>')
            elif tag in empty_elements:
                pass
            elif self.checkflag == 1:
                self.__data.append("</%s>" % tag)
        self.tagstack = self.tagstack[i+1:]

    def handle_comment(self, data):
        self.handle_data('<!--%s-->' % data)

    def handle_charref(self, name):
        """Handle character reference for UNICODE"""
        self.handle_data('&#%s;' % name)

    def handle_entityref(self, name):
        """Handle entity references.
        """
        self.handle_data('&%s;' % name)

if __name__ == '__main__':
    from sys import stdin
    data = stdin.read()

    mycleaner = HTMLCleaner('iso8859-1')
    import pdb
#   pdb.set_trace()
    res = mycleaner.clean(data)
    print res
