Readme for MailArchive

    MailArchive is a product that can let the browse a mail archive in
    Unix MBOX format. The product resyncronises every ten minutes when
    the mail files change. It is therefore maintenance free. The product
    is tested on Zope 2.7, but can be made to work on Zope 2.6.

How to use it

    First you install MailArchive-xxx.tgz in the Products folder
    and restart Zope. You will now be able to create objects of
    the type "MailArchiveFolder" The form will ask you four fields:
    the id, title, path to mail archive directory on the local disk.
    You need the "Add MailArchiveFolder" permission in order to add a
    MailArchiveFolder. Upon creation of this object, all the MBOX files
    inside this mail directory will be added to Zope.

    For more complete instructions read INSTALL.txt

Dependencies

    If you use Zope 2.6 with Python 2.1, you need the email-package and
    HTMLParser.py for Python. Download and install it (maybe as root)
    with the same python-binary you use for running your Zope-Server.

How to test it

    Set up the environment variabiles for your Zope server in the
    'run_tests.bat' file Run the tests using the 'run_tests.bat' file.
    
    Linux users should do the same operations on run_tests.sh
