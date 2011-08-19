import unittest
import SMTPDispatcher
import smtplib
import asyncore

class Catcher:
    def __init__(self):
        self.count = 0
        self.params = None
        self.kw = None
    def call(self, *params, **kw):
        self.count += 1
        self.params = params
        self.kw = kw

class TestMatcher(unittest.TestCase):

    def setUp(self):
        self.catcher = Catcher()

    def test_no_match(self):
        matcher = SMTPDispatcher.Matcher()
        matcher.register(r"\w+ \w+", self.catcher.call)

        # verify no match
        matcher.match("hello")
        self.assertEqual(self.catcher.count, 0)

    def test_match_no_params(self):
        matcher = SMTPDispatcher.Matcher()
        matcher.register(r"\w+ \w+", self.catcher.call)

        # verify match w/ no params
        matcher.match("hello world")
        self.assertEqual(self.catcher.count, 1)
        self.assertEqual(len(self.catcher.params), 0)

    def test_match_params(self):
        matcher = SMTPDispatcher.Matcher()
        matcher.register(r"(\w+) (\w+)", self.catcher.call)

        # verify match w/ no params
        matcher.match("hello world")
        self.assertEqual(self.catcher.count, 1)
        self.assertEqual(len(self.catcher.params),2)
        self.assertEqual(self.catcher.params[0], "hello")
        self.assertEqual(self.catcher.params[1], "world")

    def test_longest_match(self):
        matcher = SMTPDispatcher.Matcher()
        catcher1 = Catcher()
        matcher.register(r"[0-9]+", catcher1.call)
        catcher2 = Catcher()
        matcher.register(r"[0-9]+[a-z]+", catcher2.call)

        # verify only longest match is called
        matcher.match("0abc")
        self.assertEqual(catcher1.count,0)
        self.assertEqual(catcher2.count,1)


    def test_multiple_match(self):
        matcher = SMTPDispatcher.Matcher()
        catcher1 = Catcher()
        matcher.register(r"[0-9]+", catcher1.call)
        catcher2 = Catcher()
        matcher.register(r"[0-9]+", catcher2.call)

        # verify only first match is called if identical regexs used
        matcher.match("0123")
        self.assertEqual(catcher1.count,1)
        self.assertEqual(catcher2.count,0)

    def test_partial_match(self):
        matcher = SMTPDispatcher.Matcher()
        catcher1 = Catcher()
        matcher.register(r"[0-9]+", catcher1.call)

        # verify match works if only partial unless regex specifies
        matcher.match("0123@test.com")
        self.assertEqual(catcher1.count,1)

class SMTPHandler:
    def __init__(self):
        self.peer = None
        self.mailfrom = None
        self.mailtos = None
        self.message = None
    
    def handle(self, peer, mailfrom, mailtos, message):
        self.peer = peer
        self.mailfrom = mailfrom
        self.mailtos = mailtos
        self.message = message

import threading
import os
class MonitorThread(threading.Thread):
    def run(self):
        try:
            asyncore.loop(timeout=1)
        except:
            # dont' care if async core dies during testing
            # async core is not the UUT
            pass


class TestSMTPDispatcher(unittest.TestCase):
    def setUp(self):
        self.server = SMTPDispatcher.SMTPDispatcher(("localhost",1234), None)

    def test_single_dispatch(self):
        handler = SMTPHandler()
        self.server.route(r'.*', handler.handle)
        thd = MonitorThread()
        thd.start()

        smtp = smtplib.SMTP("localhost",1234)
        smtp.sendmail("test@test.com", "dest@test.com", "Hello")
        smtp.quit()
        self.assertEqual(handler.mailfrom, "test@test.com")
        self.assertEqual(handler.message, "Hello")

    def test_multiple_dispatch(self):
        handler1 = SMTPHandler()
        handler2 = SMTPHandler()
        self.server.route(r'[0-9]+@test.com', handler2.handle)
        self.server.route(r'[a-z]+@test.com', handler1.handle)

        thd = MonitorThread()
        thd.start()

        smtp = smtplib.SMTP("localhost",1234)
        smtp.sendmail("test@test.com", "dest@test.com", "Hello")
        smtp.quit()
        self.assertEqual(handler1.mailfrom, "test@test.com")
        self.assertEqual(handler1.message, "Hello")


    def tearDown(self):
        self.server.close()

if __name__ == '__main__':
    unittest.main()