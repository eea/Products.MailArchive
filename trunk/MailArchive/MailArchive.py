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

#Zope imports
from OFS.Image import File
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from modules.mbox import mbox
from modules.mbox_email import mbox_email

_marker = []

def to_num_ent(str):
    res = []
    for ch in str:
        och = ord(ch)
        if och < 128:
            res.append(ch)
        else:
            res.append('&#%d;' % och)
    return ''.join(res)

def addMailArchive(self, id='', title='', path='', REQUEST=None):
    """ """
    ob = MailArchive(id, title, path)
    self._setObject(id, ob)
    if REQUEST:
        return self.manage_main(self, REQUEST, update_menu=1)

class MailArchive(Folder, mbox):
    """ """

    meta_type = 'MailArchive'
    product_name = 'MailArchive'
    icon = 'misc_/MailArchive/archive.gif'

    def __init__(self, id, title, path):
        #constructor
        self.id = id
        self.title = title
        mbox.__dict__['__init__'](self, path)

    manage_options = (
        SimpleItem.manage_options
        +
        (
            {'label' : 'View', 'action' : 'index_html'},
        )
    )

    security = ClassSecurityInfo()

    def sortMboxMsgs(self, sort_by=''):
        #returns a sorted list of messages
        n = -1
        if sort_by == 'subject': n = 2
        elif sort_by == 'date': n = 3
        elif sort_by == 'author': n = 4
        elif sort_by == 'thread': n = 5
        if n > -1:
            if n == 5:
                return self.get_mbox_thread(self.sort_mbox_msgs(3))
                #return self.sort_mbox_msgs(3)
            else:
                return [(0, x) for x in self.sort_mbox_msgs(n)]
        else:
            return [(0, x) for x in self.get_mbox_msgs()]

    def processId(self, REQUEST):
        try: return abs(int(REQUEST.get('id', '')))
        except: return None

    def getMsg(self, id=None):
        #returns the body of the given message id
        if id is not None:
            m = mbox_email(self.get_mbox_msg(id))
            return (m.getAuthor(), m.getEmailFrom(), m.getSubject(), m.getDateTime(), \
                    self.parseContent(m.getContent()), m.getAttachments())
        else:
            return None

    def parseContent(self, msg):
        junks = ['<x-html>', '</x-html>', '<x-flowed>', '</x-flowed>']
        #get rid of junks
        for j in junks: msg = msg.replace(j, '')
        msg = self.newlineToBr(msg)
        msg = to_num_ent(msg)
        return self.extractUrl(msg)

    def getPrevNext(self, id, sort_by):
        #returns info about the next and previous message
        l = [x[1] for x in self.sortMboxMsgs(sort_by)]
        t = [x[0] for x in l]
        index = t.index(id)
        if index > 0: prev = l[index-1]
        else: prev = -1
        if index < len(t)-1: next = l[index+1]
        else: next = -1
        return (prev, next)

    def getMboxSize(self):
        return self.size

    def _getOb(self, id, default=_marker):
        if id.find('+++') != -1:
            info = id.split('+++')
            msg = info[0]
            att = info[1]
            if msg is not None:
                m = mbox_email(self.get_mbox_msg(int(msg)))
                data = m.getAttachment(att)
                self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=%s' % self.quote_attachment(att))
                return File(att, '', data).__of__(self)
            else:
                return None
        elif default is _marker:
            return getattr(self, id)
        else:
            return default

    security.declareProtected('View', 'index_html')
    index_html = PageTemplateFile('zpt/MailArchive_index', globals())

    security.declareProtected('View', 'message_html')
    message_html = PageTemplateFile('zpt/MailArchive_message', globals())

InitializeClass(MailArchive)
