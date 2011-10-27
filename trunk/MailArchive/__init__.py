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


from App.ImageFile import ImageFile

import MailArchiveFolder

def initialize(context):

    context.registerClass(
            MailArchiveFolder.MailArchiveFolder,
            permission='Add MailArchiveFolder',
            constructors = (
                    MailArchiveFolder.manage_addMailArchiveFolderForm,
                    MailArchiveFolder.manage_addMailArchiveFolder,
            ),
    )

misc_={
    "cabinet.gif": ImageFile("icons/cabinet.gif",globals()),
    "archive.gif": ImageFile("icons/archive.gif",globals()),
    "sortnot.gif": ImageFile("icons/sortnot.gif",globals()),
    "sortup.gif": ImageFile("icons/sortup.gif",globals()),
    "sortdown.gif": ImageFile("icons/sortdown.gif",globals()),
}
