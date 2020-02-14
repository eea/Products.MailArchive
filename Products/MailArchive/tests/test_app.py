# acceptance tests
import os
import sys
import Zope
import transaction
from Testing.makerequest import makerequest
from Testing import ZopeTestCase
from Products.MailArchive.MailArchiveFolder import MailArchiveFolder

if __name__ == '__main__':
    exec(compile(open(os.path.join(sys.path[0], 'framework.py'), "rb").read(),
                 os.path.join(sys.path[0], 'framework.py'), 'exec'))


# constants
INSTANCE_HOME = os.environ.get('INSTANCE_HOME', '')
MBOX = 'mail_archive'
MBOX_PATH = os.path.join(INSTANCE_HOME,
                         r'Products/MailArchive/tests/data/mbox_directory')

get_transaction = transaction.get


class Test01_MboxPreviousNext(ZopeTestCase.ZopeTestCase):
    def setUp(self):
        self.app = makerequest(Zope.app())
        get_transaction().begin()
        self.mbox = MailArchiveFolder(MBOX, '', MBOX_PATH, 0, '', '')
        self.app._setObject(MBOX, self.mbox)

    def test_prev_next_first(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        prev, next = obj.getPrevNext(
            '815f70cf050329015744ac9a43', 'subject', 0)
        id = obj.get_msg_id(prev)
        self.assertEqual(id, '<815f70cf05033023503b4a9704@mail.gmail.com>')
        self.assertEqual(next, -1)
        prev, next = obj.getPrevNext(
            '815f70cf050329015744ac9a43', 'subject', 1)
        id = obj.get_msg_id(next)
        self.assertEqual(prev, -1)
        self.assertEqual(id, '<815f70cf05033023503b4a9704@mail.gmail.com>')

    def test_prev_next_middle(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        prev, next = obj.getPrevNext('775606', 'date', 0)
        prev = obj.get_msg_id(prev)
        next = obj.get_msg_id(next)
        self.assertEqual(prev, '<424A5688.6050106@microsfot.co.uk>')
        self.assertEqual(next, '<815f70cf05033023503b4a9704@mail.gmail.com>')
        prev, next = obj.getPrevNext('775606', 'date', 1)
        prev = obj.get_msg_id(prev)
        next = obj.get_msg_id(next)
        self.assertEqual(prev, '<815f70cf05033023503b4a9704@mail.gmail.com>')
        self.assertEqual(next, '<424A5688.6050106@microsfot.co.uk>')

    def test_prev_next_last(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        prev, next = obj.getPrevNext('6050106', 'subject', 0)
        next = obj.get_msg_id(next)
        self.assertEqual(prev, -1)
        self.assertEqual(next,
                         '<16970.59764.819866.775606@gargle.gargle.HOWL>')
        prev, next = obj.getPrevNext('6050106', 'subject', 1)
        prev = obj.get_msg_id(prev)
        self.assertEqual(prev,
                         '<16970.59764.819866.775606@gargle.gargle.HOWL>')
        self.assertEqual(next, -1)

    def tearDown(self):
        self.app._delObject(MBOX)
        self.mbox = None
        get_transaction().abort()
        self.app._p_jar.close()


class Test02_MboxAddRemoveModify(ZopeTestCase.ZopeTestCase):
    def setUp(self):
        self.app = makerequest(Zope.app())
        get_transaction().begin()
        self.mbox = MailArchiveFolder(MBOX, '', MBOX_PATH, 0, '', '')
        self.app._setObject(MBOX, self.mbox)

    def add_mbox(self):
        f = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "r")  # noqa: w605
        content = ''.join([x for x in f.readlines()][1:])
        f.close()
        c = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "w")  # noqa: w605
        c.write(content)
        c.close()

    def del_mbox(self):
        f = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "r")  # noqa: w605
        content = ''.join([x for x in f.readlines()])
        f.close()
        c = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "w")  # noqa: w605
        c.write("<marker>\n%s" % content)
        c.close()

    def change_mbox_size(self):
        self.add_mbox()
        f = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "a")  # noqa: w605
        f.write('\n<marker>')
        f.close()

    def revert_mbox_size(self):
        f = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "r")  # noqa: w605
        content = ''.join([x for x in f.readlines()][:-1])
        f.close()
        c = open("%s\%s" % (MBOX_PATH, 'mbox3.mbx'), "w")  # noqa: w605
        c.write(content)
        c.close()
        self.del_mbox()

    """
    The product has to automatically detect when new mailboxes
    appear in the directory it tracks"""
    def test_detect_add(self):
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox1.mbx', 'mbox2.mbx'])
        self.add_mbox()
        self.mbox.updateArchives(0)
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox3.mbx', 'mbox1.mbx', 'mbox2.mbx'])
        self.del_mbox()

    """
    The product has to automatically detect
    when mailboxes are deleted in the directory. """
    def test_detect_delete(self):
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox1.mbx', 'mbox2.mbx'])
        self.add_mbox()
        self.mbox.updateArchives(0)
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox3.mbx', 'mbox1.mbx', 'mbox2.mbx'])
        self.del_mbox()
        self.mbox.updateArchives(0)
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox1.mbx', 'mbox2.mbx'])

    """
    If a mailbox changes in size or last modification date
    then the system has to automatically reload the mailbox. """
    def test_detect_modification(self):
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox1.mbx', 'mbox2.mbx'])
        self.change_mbox_size()  # change mbox size
        self.mbox.updateArchives(0)
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        self.assertEqual(ids, ['mbox3.mbx', 'mbox1.mbx', 'mbox2.mbx'])
        self.revert_mbox_size()  # revert changes

    def tearDown(self):
        self.app._delObject(MBOX)
        self.mbox = None
        get_transaction().abort()
        self.app._p_jar.close()


class Test03_ArchiveMbox(ZopeTestCase.ZopeTestCase):
    def setUp(self):
        self.app = makerequest(Zope.app())
        get_transaction().begin()
        self.mbox = MailArchiveFolder(MBOX, '', MBOX_PATH, 0, '', '')
        self.app._setObject(MBOX, self.mbox)

    def test_filter_mboxes(self):
        obj = self.mbox.getArchives()[1]    # only mbox2.mbx
        for s in [obj.get_msg_subject(x[1]) for x in
                  obj.sortMboxMsgs('subject')]:
            self.failIfEqual(
                s, "DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA")

    def tearDown(self):
        self.app._delObject(MBOX)
        self.mbox = None
        get_transaction().abort()
        self.app._p_jar.close()


class Test04_MboxSorted(ZopeTestCase.ZopeTestCase):
    def setUp(self):
        self.app = makerequest(Zope.app())
        get_transaction().begin()
        self.mbox = MailArchiveFolder(MBOX, '', MBOX_PATH, 0, '', '')
        self.app._setObject(MBOX, self.mbox)

    def tearDown(self):
        self.app._delObject(MBOX)
        self.mbox = None
        get_transaction().abort()
        self.app._p_jar.close()

    """ List of archives should be sorted on date of the first message
        - newest first. """
    def test_sort_archives(self):
        objs = self.mbox.getArchives()
        ids = [x.id for x in objs]
        start = [x.starting for x in objs]
        self.assertEqual(start, [(2005, 3, 29, 1, 57, 52, 0, 0, 0),
                                 (2003, 9, 11, 11, 18, 25, 0, 0, 0)])
        self.assertEqual(ids, ['mbox1.mbx', 'mbox2.mbx'])

    def test_sort_author_ascendent(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('author')
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<424A5688.6050106@microsfot.co.uk>',
            '<815f70cf050329015744ac9a43@mail.gmail.com>',
            '<815f70cf05033023503b4a9704@mail.gmail.com>',
            '<16970.59764.819866.775606@gargle.gargle.HOWL>'])

    def test_sort_author_descendent(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('author', 1)
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<16970.59764.819866.775606@gargle.gargle.HOWL>',
            '<815f70cf05033023503b4a9704@mail.gmail.com>',
            '<815f70cf050329015744ac9a43@mail.gmail.com>',
            '<424A5688.6050106@microsfot.co.uk>'])

    def test_sort_subject_ascendent(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('subject')
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<424A5688.6050106@microsfot.co.uk>',
            '<16970.59764.819866.775606@gargle.gargle.HOWL>',
            '<815f70cf05033023503b4a9704@mail.gmail.com>',
            '<815f70cf050329015744ac9a43@mail.gmail.com>'])

    def test_sort_subject_descendent(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('subject', 1)
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<815f70cf050329015744ac9a43@mail.gmail.com>',
            '<815f70cf05033023503b4a9704@mail.gmail.com>',
            '<16970.59764.819866.775606@gargle.gargle.HOWL>',
            '<424A5688.6050106@microsfot.co.uk>'])

    def test_sort_date_ascendent(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('date')
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<815f70cf050329015744ac9a43@mail.gmail.com>',
            '<424A5688.6050106@microsfot.co.uk>',
            '<16970.59764.819866.775606@gargle.gargle.HOWL>',
            '<815f70cf05033023503b4a9704@mail.gmail.com>'])

    def test_sort_date_descendent(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('date', 1)
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<815f70cf05033023503b4a9704@mail.gmail.com>',
            '<16970.59764.819866.775606@gargle.gargle.HOWL>',
            '<424A5688.6050106@microsfot.co.uk>',
            '<815f70cf050329015744ac9a43@mail.gmail.com>'])

    def test_sort_thread(self):
        obj = self.mbox.getArchives()[0]    # only mbox1.mbx
        msgs_sorted = obj.sortMboxMsgs('thread')
        msgs_sorted_ids = [obj.get_msg_id(x[1]) for x in msgs_sorted]
        self.assertEqual(msgs_sorted_ids, [
            '<815f70cf050329015744ac9a43@mail.gmail.com>',
            '<424A5688.6050106@microsfot.co.uk>',
            '<16970.59764.819866.775606@gargle.gargle.HOWL>',
            '<815f70cf05033023503b4a9704@mail.gmail.com>'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test01_MboxPreviousNext))
    suite.addTest(makeSuite(Test02_MboxAddRemoveModify))
    suite.addTest(makeSuite(Test03_ArchiveMbox))
    suite.addTest(makeSuite(Test04_MboxSorted))
    return suite
