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
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from modules.mbox import mbox
from modules.mbox_email import mbox_email

_marker = []

def addMailArchive(self, id='', title='', path='', REQUEST=None):
    """ """
    ob = MailArchive(id, title, path)
    if len(ob.cache.keys()) > 0:
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

    security.declareProtected(view, 'sortMboxMsgs')
    def sortMboxMsgs(self, skey='', rkey=''):
        #returns a sorted list of messages
        n = -1
        if skey == 'subject': n = 3
        elif skey == 'date': n = 4
        elif skey == 'author': n = 5
        elif skey == 'thread': n = 6
        if n > -1:
            if n == 6:
                return self.get_mbox_thread(self.sort_mbox_msgs(4, ''))
            elif n == 5:
                return [(0, x) for x in self.sort_mbox_msgs_ci(n, rkey)]
            else:
                return [(0, x) for x in self.sort_mbox_msgs(n, rkey)]
        else:
            return [(0, x) for x in self.get_mbox_msgs()]


    security.declareProtected(view, 'getMailArhiveURL')
    def getMailArhiveURL(self):
        """ return the absolute path to this MailArchive """
        return self.absolute_url()

    security.declareProtected(view, 'getMsg')
    def getMsg(self, id=None):
        #returns the body of the given message id
        if id is not None:
            m = mbox_email(self.get_mbox_msg(id))
            if m.getMessageID():
                return (m.getFrom(), m.getTo(), m.getCC(), m.getSubject(), m.getDateTime(), \
                        m.getContent(), m.getAttachments())

    security.declareProtected(view, 'getPrevNext')
    def getPrevNext(self, id, skey, rkey):
        #returns info about the next and previous message
        l = [x[1] for x in self.sortMboxMsgs(skey, rkey)]
        t = [x[0] for x in l]
        index = t.index(id)
        if index > 0: prev = l[index-1]
        else: prev = -1
        if index < len(t)-1: next = l[index+1]
        else: next = -1
        return (prev, next)

    security.declareProtected(view, 'getMboxSize')
    def getMboxSize(self):
        return self.size

    #We don't really care about the download of the mailboxes.
    #The mbox format is little used outside the Unix community.

    def _getOb(self, id, default=_marker):
        if id.find('+++') != -1:
            info = id.split('+++')
            msg = info[0]
            att = info[1]
            if msg is not None:
                m = mbox_email(self.get_mbox_msg(msg))
                data = m.getAttachment(att)
                self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=%s' % self.quote_attachment(att))
                return File(att, '', data).__of__(self)
            else:
                return None
        else:
            return getattr(self, id)

    security.declareProtected('View', 'index_html')
    index_html = PageTemplateFile('zpt/MailArchive_index', globals())

    security.declareProtected('View', 'message_html')
    message_html = PageTemplateFile('zpt/MailArchive_message', globals())

InitializeClass(MailArchive)
