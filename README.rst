===========
MailArchive
===========

.. Contents ::

What is MailArchive?
--------------------

    MailArchive is a product that can let the browse a mail archive in
    Unix MBOX format or connect to an IMAP account. The product resyncronises
    every ten minutes when the mail files change. It is therefore maintenance free.
    The product is tested on Zope 2.12, but can be made to work on Zope 2.6.


How to use it
-------------

    First you install Products.MailArchive in the Products folder
    and restart Zope. You will now be able to create objects of
    the type "MailArchiveFolder" The form will ask you for some fields:
    the id, title, path to mail archive directory on the local disk,
    IMAP connection values.
    You need the "Add MailArchiveFolder" permission in order to add a
    MailArchiveFolder. Upon creation of this object, all the MBOX files
    inside this mail directory will be added to Zope.

    For more complete instructions read docs/INSTALL.txt

Dependencies
------------

    This package works with Zope 2.12 and Python 2.7.

How to test it
--------------

    Set up the environment variabiles for your Zope server in the
    'run_tests.bat' file Run the tests using the 'run_tests.bat' file.
    
    Linux users should do the same operations on run_tests.sh
