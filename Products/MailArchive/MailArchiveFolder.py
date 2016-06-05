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
from OFS.Folder import Folder
from OFS.Image import File
from Globals import InitializeClass, MessageDialog
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from AccessControl import Unauthorized
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from MailArchive import addMailArchive, addMailArchiveIMAP
from Utils import Utils
from modules.imap_client import imap_client

_marker = []

manage_addMailArchiveFolderForm = PageTemplateFile('zpt/MailArchiveFolder_add', globals())
def manage_addMailArchiveFolder(self, id, title='', path='', allow_zip=0, index_header='', index_footer='',
    imap_servername='', imap_username='', imap_password='', REQUEST=None):
    """ Add a new MailArchiveFolder object """

    ob = MailArchiveFolder(id, title, path, allow_zip, index_header, index_footer,
        imap_servername, imap_username, imap_password)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    
class MailArchiveFolder(Folder, Utils):
    """ """
    meta_type = 'MailArchiveFolder'
    product_name = 'MailArchive'
    icon='misc_/MailArchive/cabinet.gif'
    
    manage_options = (
        Folder.manage_options[:2]
        +
        (
            {'label' : 'Properties', 'action' : 'properties_html'},
        )
        +
        Folder.manage_options[3:-2]
    )

    security = ClassSecurityInfo()

    def __init__(self, id, title, path, allow_zip, index_header, index_footer,
        imap_servername, imap_username, imap_password):
        self.id = id
        self.title = title
        self._path = path

        #We don't really care about the download of the mailboxes.
        #The mbox format is little used outside the Unix community.
        self.allow_zip = 0  #allow_zip
        self.mbox_ignore = ['Trash','Sent','Sent-Items'] 
        self.index_header = index_header
        self.index_footer = index_footer
        self._v_last_update = 0

        #imap
        self.imap_servername = imap_servername
        self.imap_username = imap_username
        self.imap_password = imap_password

    def __setstate__(self,state):
        MailArchiveFolder.inheritedAttribute("__setstate__") (self, state)
        self._v_last_update = 0
        if not hasattr(self, 'allow_zip'):
            self.allow_zip = 0
        if not hasattr(self, 'index_header'):
            self.index_header = ''
        if not hasattr(self, 'index_footer'):
            self.index_footer = ''
        if not hasattr(self, 'mbox_ignore'):
            self.mbox_ignore = ['Trash','Sent','Sent-Items']
        if not hasattr(self, 'imap_servername'):
            self.imap_servername = ''
        if not hasattr(self, 'imap_username'):
            self.imap_username = ''
        if not hasattr(self, 'imap_password'):
            self.imap_password = ''

    security.declareProtected(view, 'get_mailarchivefolder_path')
    def get_mailarchivefolder_path(self, p=0):
        return self.absolute_url(p)

    security.declareProtected(view, 'getPath')
    def getPath(self):
        return self._path

    security.declareProtected(view_management_screens, 'validPath')
    def validPath(self):
        return self.valid_directory(self._path)

    security.declareProtected(view, 'getArchives')
    def getArchives(self):
        """ returns the archives list sorted by the 'starting' property
            - the date of the first message in the mbox file """
        l = [(x.starting, x) for x in self.objectValues(['MailArchive', 'MailArchiveIMAP'])]
        l.sort()
        l.reverse()
        return [val for (key, val) in l]

    security.declarePrivate('_delete_archives')
    def _delete_archives(self, archives, mboxes):
        """ If a mailbox file disappears from the file system
         it shall disappear here also """
        del_objs = self.list_difference(archives, mboxes)
        del_objs.extend(self.mbox_ignore)
        #check if objects are in Zope to avoid AttributeError
        buf = [ x for x in del_objs if hasattr(self, x) ]
        self.manage_delObjects(self.remove_duplicates(buf))

    security.declarePrivate('_add_archives')
    def _add_archives(self, mboxes):
        """ add mailboxes """
        for mb in mboxes:
            try:
                addMailArchive(self, mb[1], '', mb[0])
            except:
                pass

    security.declarePrivate('_reload_archive')
    def _reload_archives(self, zobjs, mboxes):
        """ reload archives """
        [ self.manage_delObjects(mbox[1]) for mbox in mboxes if mbox[1] in zobjs]
        self._add_archives(mboxes)

    security.declarePrivate('_load_archives')
    def _load_archives(self):
        """ Load the mail archives located on the file system.
            This function is called when a new MailArchiveFolder
            instance is created.
        """

        #Local filesystem mboxes
        path = self.getPath()
        if self.valid_directory(path):
            mboxes, others = self.get_mboxes(path, self.mbox_ignore)    #mbox archives
            self._add_archives(mboxes)

        #IMAP mailboxes
        imap_client_ob = self.create_imap_client()
        mboxes = imap_client_ob.listMailboxes(self.mbox_ignore)
        self._add_archives_imap(mboxes, imap_client_ob)

        self.kill_imap_client(imap_client_ob)

    security.declarePrivate('_add_archives_imap')
    def _add_archives_imap(self, mboxes, imap_client_ob):
        """ add mailboxes for imap """
        for mb in mboxes:
            try:
                addMailArchiveIMAP(self, imap_client_ob, mb, '', mb)
            except:
                pass

    security.declarePrivate('_reload_archives_imap')
    def _reload_archives_imap(self, zobjs, mboxes, imap_client_ob):
        """ reload archives for imap """
        [self.manage_delObjects(mbox) for mbox in mboxes if mbox in zobjs]
        self._add_archives_imap(mboxes, imap_client_ob)

    security.declareProtected(view, 'updateArchives')
    def updateArchives(self, delay=1):
        """ Update the mail archives
            Only check the mailboxes every 10th minute.
            FIXME: To be called from MailArchiveFolder_index.zpt
                (preferably while the user sees the list)
        """
        if delay and self._v_last_update > self.get_time() - 600:
            return
        self._v_last_update = self.get_time()

        #Local filesystem mboxes
        path = self.getPath()
        if self.valid_directory(path):
            ids = self.objectIds(['MailArchive']) #zope archives
            mboxes, others = self.get_mboxes(path, self.mbox_ignore)    #mbox archives
            self._delete_archives(ids, [mb[1] for mb in mboxes])

            buf = []
            for mbox in mboxes:
                if hasattr(self, mbox[1]):
                    m = getattr(self, mbox[1])
                    # If the mailbox file already exists on the filesystem and
                    # it hasn't changed, then don't read it again
                    if m.size != self.get_mbox_size(mbox[0]) and m.last_modified != self.get_last_modif(mbox[0]):
                        buf.append(mbox)
                else:
                    buf.append(mbox)
            self._reload_archives(ids, buf)

        #IMAP maillboxes
        imap_client_ob = self.create_imap_client()
        mboxes = imap_client_ob.listMailboxes(self.mbox_ignore)

        #get zope archives and remove mailboxes that no longer exists
        ids = self.objectIds(['MailArchiveIMAP'])
        self._delete_archives(ids, mboxes)
        self._reload_archives_imap(ids, mboxes, imap_client_ob)

        self.kill_imap_client(imap_client_ob)

    security.declareProtected(view_management_screens, 'listMailboxes')
    def listMailboxes(self):
        """ list all mboxes from directory """
        res = []
        mboxes, others = self.get_mboxes(self._path, ignore_list=[])
        res = ["%s *" % mbox[1] for mbox in mboxes]
        res.extend([oth[1] for oth in others])
        res.sort()
        return res

    #We don't really care about the download of the mailboxes.
    #The mbox format is little used outside the Unix community.
    
    #def _getOb(self, id, default=_marker):
    #    if id.endswith(".zip"):
    #        if not self.allow_zip:
    #            self.RESPONSE.setStatus(404, "Not Found")
    #            return self.RESPONSE
    #        mbox_id = id[:-4]
    #        #get mbox content
    #        obj = self._getOb(mbox_id)
    #        mbox = obj.get_mbox_file()
    #        #zip mbox content
    #        zf, path = self.zip_file(id, mbox_id, mbox)
    #        self.delete_file(path)
    #        self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/x-zip-compressed')
    #        self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment')
    #        return File(id, '', zf, content_type='application/x-zip-compressed').__of__(self)
    #    else:
    #        return getattr(self, id)

    #IMAP API
    security.declareProtected(view_management_screens, 'has_imap_settings')
    def has_imap_settings(self):
        return hasattr(self, 'imap_servername')

    security.declareProtected(view_management_screens, 'manageIMAPSettings')
    def manageIMAPSettings(self, REQUEST=None, RESPONSE=None):
        """ Run this for upgrading with imap functionality """
        if not self.has_imap_settings():
            self.imap_servername = ''
            self.imap_username = ''
            self.imap_password = ''
            self._p_changed = 1
        if REQUEST is not None:
            return MessageDialog(title = 'Upgraded',
                message = "The IMAP settings %s have been set!" % self.id,
                action = './manage_main',
                )

    def create_imap_client(self):
        imap_client_ob = imap_client(self.imap_servername, self.imap_username, self.imap_password)
        imap_client_ob.connOpen()
        return imap_client_ob

    def kill_imap_client(self, imap_client_ob):
        imap_client_ob.connClose()
        imap_client_ob = None

    security.declareProtected(view_management_screens, 'valid_imap_conn')
    def valid_imap_conn(self, imap_client_ob=None):
        flg_close = 0
        if imap_client_ob is None: flg_close, imap_client_ob = 1, self.create_imap_client()
        r = imap_client_ob.connValid()
        if flg_close: self.kill_imap_client(imap_client_ob)
        return r

    security.declareProtected(view, 'list_imap_mailboxes')
    def list_imap_mailboxes(self, imap_client_ob=None, ignore_list=[]):
        #returns a list of available mailboxes
        #(e.g. ['INBOX', 'INBOX.Drafts', ..]
        flg_close = 0
        if imap_client_ob is None: flg_close, imap_client_ob = 1, self.create_imap_client()
        r = imap_client_ob.listMailboxes(ignore_list)
        if flg_close: self.kill_imap_client(imap_client_ob)
        return r

    security.declareProtected(view, 'show_imap_mailboxes')
    def show_imap_mailboxes(self, imap_client_ob=None):
        return self.list_to_lines(self.list_imap_mailboxes(imap_client_ob))

    security.declareProtected(view, 'list_imap_mailboxes_ex')
    def list_imap_mailboxes_ex(self, imap_client_ob=None, ignore_list=[]):
        #returns a list of available mailboxes and the number of messages
        #(e.g. [{'name': 'INBOX', 'counter': 457}, {'name': INBOX.Drafts', 'counter': 0}, ..]
        flg_close = 0
        if imap_client_ob is None: flg_close, imap_client_ob = 1, self.create_imap_client()
        r = imap_client_ob.listMailboxesEx(ignore_list)
        if flg_close: self.kill_imap_client(imap_client_ob)
        return r

    security.declareProtected(view, 'show_imap_mailboxes_ex')
    def show_imap_mailboxes_ex(self, imap_client_ob=None):
        return self.list_to_lines(['%s (%s)' % (x['name'], x['counter']) for x in self.list_imap_mailboxes_ex(imap_client_ob)])

    #ZMI
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', path='', mbox_ignore=[], index_header='', index_footer='',
             allow_zip=0, imap_servername='', imap_username='', imap_password='', REQUEST=None):
        """ save properties """
        self.title = title
        self._path = path.strip()
        self.allow_zip = allow_zip
        self.mbox_ignore = self.lines_to_list(mbox_ignore)
        self.index_header = index_header
        self.index_footer = index_footer
        self.imap_servername = imap_servername.strip()
        self.imap_username = imap_username.strip()
        self.imap_password = imap_password.strip()
        self.updateArchives(0)
        self._p_changed = 1
        if REQUEST is not None:
            return MessageDialog(title = 'Edited',
                message = "The properties of %s have been changed!" % self.id,
                action = './manage_main',
                )

    security.declareProtected(view_management_screens, 'manage_afterAdd')
    def manage_afterAdd(self, item, container, new_fn=None):
        self._load_archives()
        Folder.inheritedAttribute ("manage_afterAdd") (self, item, container)

    security.declareProtected(view_management_screens, 'properties_html')
    properties_html = PageTemplateFile('zpt/MailArchiveFolder_props', globals())

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/MailArchiveFolder_index', globals())

    security.declareProtected(view, 'index_xslt')
    index_xslt = PageTemplateFile('zpt/MailArchiveFolder_xslt', globals())

    security.declareProtected(view, 'index_rdf')
    def index_rdf(self, REQUEST=None, RESPONSE=None):
        """ """
        #process items for the RDF file
        l_archives = self.getArchives()
        if len(l_archives)>0:
            l_archive = l_archives[0]
            l_msgs = l_archive.sortMboxMsgs('date', '1')[:10]
            #generate RDF file
            l_rdf = []
            l_rdf_append = l_rdf.append
            l_rdf_append('<?xml version="1.0" encoding="utf-8"?>')
            l_rdf_append('<?xml-stylesheet type="text/xsl" href="%s/index_xslt"?>' % self.absolute_url())
            l_rdf_append('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns="http://purl.org/rss/1.0/">')
            l_rdf_append('<channel rdf:about="%s">' % self.absolute_url())
            l_rdf_append('<title>%s</title>' % self.xmlEncode(self.title_or_id()))
            l_rdf_append('<link>%s</link>' % self.absolute_url())
            l_rdf_append('<items>')
            l_rdf_append('<rdf:Seq>')
            for l_depth, l_msg in l_msgs:
                l_rdf_append('<rdf:li resource="%s/message_html?skey=date&amp;id=%s"/>' % (l_archive.absolute_url(), l_archive.get_msg_index(l_msg)))
            l_rdf_append('</rdf:Seq>')
            l_rdf_append('</items>')
            l_rdf_append('</channel>')
            descr = []
            for l_depth, l_msg in l_msgs:
                for addr in l_archive.get_msg_to(l_msg):
                    if addr[0]: descr.append(addr[0])
                    else:   descr.append(addr[1])
                for addr in l_archive.get_msg_cc(l_msg):
                    if addr[0]: descr.append(addr[0])
                    else:   descr.append(addr[1])
                l_rdf_append('<item rdf:about="%s/message_html?skey=date&amp;id=%s">' % (l_archive.absolute_url(), l_archive.get_msg_index(l_msg)))
                l_rdf_append('<title>%s</title>' % self.xmlEncode(l_archive.get_msg_subject(l_msg)))
                l_rdf_append('<dc:creator>%s</dc:creator>' % self.xmlEncode(l_archive.get_msg_from(l_msg)))
                l_rdf_append('<link>%s/message_html?skey=date&amp;id=%s</link>' % (l_archive.absolute_url(), l_archive.get_msg_index(l_msg)))
                l_rdf_append('<description>%s</description>' % (self.xmlEncode(', '.join(descr))))
                l_rdf_append('<dc:date>%s</dc:date>' % self.tupleToDateHTML(l_archive.get_msg_date(l_msg)))
                l_rdf_append('</item>')
            l_rdf_append("</rdf:RDF>")
            RESPONSE.setHeader('content-type', 'text/xml')
            return '\n'.join(l_rdf)
        else:
            RESPONSE.setStatus('NotFound')
            return RESPONSE

InitializeClass(MailArchiveFolder)
