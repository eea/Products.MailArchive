Readme for MailArchive

    MailArchive is a product that can let the browse a mail archive in MBOX format.


How to use it

    First you install MailArchive-xxx.tgz in the Products folder and restart
    Zope. You will now be able to create objects of the type "MailArchiveFolder"
    The form will ask you four fields: the id, title, path to mail archive on the
    local disk.  You need the "Add MailArchiveFolder" permission in order to add
    a MailArchiveFolder. Upon creation of this object, all the MBOX files inside
    this mail archive will be added to Zope.

    For more complete instructions read INSTALL.txt

Dependencies

    MailArchive requires the email-package for Python. Download and install it
    (maybe as root) with the same python-binary you use for running your Zope-Server.
    If you run Zope with Python 2.2.3 or higher, the email-package is already included.

How to test it

    Run test_email.py from MailArchive directory: python tests/test_email.py
