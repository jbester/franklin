import unittest
import SMTPDispatcher


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

         

if __name__ == '__main__':
    unittest.main()