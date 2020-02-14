import os
import sys
from Testing import ZopeTestCase
from Products.MailArchive.modules.mbox_email import mbox_email

if __name__ == '__main__':
    exec(compile(open(os.path.join(sys.path[0], 'framework.py'), "rb").read(),
                 os.path.join(sys.path[0], 'framework.py'), 'exec'))


INSTANCE_HOME = os.environ.get('INSTANCE_HOME', '')
MSG_PATH = os.path.join(INSTANCE_HOME, r'Products/MailArchive/tests/data')


class Test_MboxEmail(ZopeTestCase.ZopeTestCase):

    def open_msg(self, msg):
        path = os.path.join(MSG_PATH, msg)
        return open(path).read()

    def open_file(self, name):
        path = os.path.join(MSG_PATH, name)
        return open(path, 'rb').read()

    def test_get_to(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getTo(), [(u'John Doe', 'john.doe@fns.ro')])

    def test_get_to_with_encoding(self):
        msg = mbox_email(self.open_msg('msg2.txt'))
        self.assertEqual(msg.getTo(),
                         [(u'Tim Terleg&#229;rd', 'timte878@student.se')])

    def test_get_multiple_to(self):
        msg = mbox_email(self.open_msg('msg3.txt'))
        self.assertEqual(msg.getTo(),
                         [(u'te Kelrg', 'Je.Kelrg@ee.int'),
                          (u'NFP', 'eiofp@roleeion.int'),
                          (u'Ulri tark', 'stk@sa.sk'),
                          (u'Schnder J&#252;rn', 'juen.schder@umweltamt.at')])

    def test_get_to_with_wrong_encoding(self):
        msg = mbox_email(self.open_msg('msg4.txt'))
        self.assertEqual(msg.getTo(), [('', 'jorg.lan@iod.dk')])

    def test_get_from(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getFrom(), (u'Smith', 'john@fns.ro'))

    def test_get_from_with_encoding(self):
        msg = mbox_email(self.open_msg('msg2.txt'))
        self.assertEqual(msg.getFrom(),
                         (u'Geir B&#230;kholt', 'lists@elvww.com'))

    def test_get_from_with_wrong_encoding(self):
        msg = mbox_email(self.open_msg('msg4.txt'))
        self.assertEqual(msg.getFrom(), ('', 'linong@upu.cn'))

    def test_get_subject(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getSubject(), u'Re: test email')

    def test_get_subject_with_encoding(self):
        msg = mbox_email(self.open_msg('msg2.txt'))
        self.assertEqual(
            msg.getSubject(),
            u'[Zope] FYI:Portall&#246;sungen f&#252;r den Bildungsbereich /'
            u'  Zope Tagung (German)')

    def test_get_subject_with_wrong_encoding(self):
        msg = mbox_email(self.open_msg('msg4.txt'))
        self.assertEqual(msg.getSubject(), '')

    def test_get_date(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getDateTime(), (2005, 6, 21, 16, 11, 4, 0, 0, 0))

    def test_get_cc(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getCC(), [('', 'nick.cave@fns.ro')])

    def test_get_multiple_cc(self):
        msg = mbox_email(self.open_msg('msg3.txt'))
        self.assertEqual(msg.getCC(),
                         [(u'te Kelrg', 'Je.Kelrg@ee.int'),
                          (u'NFP', 'eiofp@roleeion.int'),
                          (u'Ulri tark', 'stk@sa.sk'),
                          (u'Schnder J&#252;rn', 'juen.schder@umweltamt.at')])

    def test_get_cc_with_encoding(self):
        msg = mbox_email(self.open_msg('msg2.txt'))
        self.assertEqual(msg.getCC(),
                         [(u'Aur&#233;lien Camp&#233;as', 'aure.aa@wanoo.fr')])

    def test_get_cc_with_wrong_encoding(self):
        msg = mbox_email(self.open_msg('msg4.txt'))
        self.assertEqual(msg.getCC(), [('', 'linong@upu.cn')])

    def test_get_in_reply_to(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getInReplyTo(), '<42B812A3.8010205@fns.ro>')

    def test_get_message_id(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getMessageID(), '<42B811E8.7090602@fns.ro>')

    def test_get_content(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(
            msg.getContent(),
            '<div style="font-family: \'Courier New\', monospace; '
            'white-space: pre-wrap">test content<br /></div>')

    def test_get_content_with_encoding(self):
        msg = mbox_email(self.open_msg('msg2.txt'))
        self.assertEqual(
            msg.getContent(),
            '<div style="font-family: \'Courier New\', monospace; '
            'white-space: pre-wrap">Urspr&#252;ngliche Nachricht<br /></div>')

    def test_list_attachments(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        self.assertEqual(msg.getAttachments(), [('test.png', 'test.png')])

    def test_list_multiple_attachments(self):
        msg = mbox_email(self.open_msg('msg3.txt'))
        self.assertEqual(msg.getAttachments(), [('test.png', 'test.png'),
                                                ('test.zip', 'test.zip')])

    def test_not_attachments(self):
        msg = mbox_email(self.open_msg('msg2.txt'))
        self.assertEqual(msg.getAttachments(), [])

    def test_get_attachment(self):
        msg = mbox_email(self.open_msg('msg1.txt'))
        target = self.open_file('test.png')
        self.assertEqual(msg.getAttachment('test.png'), target)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test_MboxEmail))
    return suite
