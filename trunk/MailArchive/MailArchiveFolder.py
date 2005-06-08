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

import os

from OFS.Folder import Folder
from OFS.Image import File
from Globals import InitializeClass, MessageDialog
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from MailArchive import addMailArchive
from Utils import Utils

_marker = []

manage_addMailArchiveFolderForm = PageTemplateFile('zpt/MailArchiveFolder_add', globals())
def manage_addMailArchiveFolder(self, id, title='', path='', REQUEST=None):
    """ Add a new MailArchiveFolder object """

    ob = MailArchiveFolder(id, title, path)
    self._setObject(id, ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    
    
class MailArchiveFolder(Folder, Utils):
    """ """
    meta_type = 'MailArchiveFolder'
    product_name = 'MailArchive'
    icon='misc_/MailArchive/folder.gif'
    
    manage_options = (
        Folder.manage_options[:2]
        +
        (
            {'label' : 'Properties', 'action' : 'properties_html'},
        )
        +
        Folder.manage_options[3:-2]
    )

    def __init__(self, id, title, path):
        self.id = id
        self.title = title
        self._path = path
    
    def getPath(self):
        return self._path

    def validPath(self):
        if not os.path.isdir(self._path):
            return 0
        return 1
    
    def getArchives(self):
        """ returns the archives list """
        return self.objectValues('MailArchive')
    
    def load_archive(self):
        """ load MailArchves """
        if not self.validPath():
            return
        mbx = []
        for f in os.listdir(self._path):
            if f.endswith('.mbx'):
                abs_path = os.path.join(self._path, f)
                addMailArchive(self, f[:-4], '', abs_path)

    def _getOb(self, id, default=_marker):
        if id.endswith(".zip"):
            mbox_id = id[:-4]
            #get mbox content
            obj = self._getOb(mbox_id)
            mbox = obj.get_mbox_file()
            #zip mbox content
            original = "%s.mbx" % mbox_id
            zf, path = self.zip_file(id, original, mbox)
            os.unlink(path)
            self.REQUEST.RESPONSE.setHeader('Content-Type', 'application/x-zip-compressed')
            self.REQUEST.RESPONSE.setHeader('Content-Disposition', 'attachment')
            return File(id, '', zf, content_type='application/x-zip-compressed').__of__(self)
        elif default is _marker:
            return getattr(self, id)
        else:
            return default

    def manageProperties(self, title='', path='', REQUEST=None):
        """ save properties """
        self.title = title
        self._path = path
        self._p_changed = 1
        self.load_archive()
        if REQUEST is not None:
            return MessageDialog(title = 'Edited',
                message = "The properties of %s have been changed!" % self.id,
                action = './manage_main',
                )
        
    def manage_afterAdd(self, item, container, new_fn=None):
        self.load_archive()
        Folder.inheritedAttribute ("manage_afterAdd") (self, item, container)

    properties_html = PageTemplateFile('zpt/MailArchiveFolder_props', globals())
    index_html = PageTemplateFile('zpt/MailArchiveFolder_index', globals())
    
InitializeClass(MailArchiveFolder)