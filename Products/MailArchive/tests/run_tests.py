import os, sys

if __name__ == '__main__':
    exec(compile(open(os.path.join(sys.path[0], 'framework.py'), "rb").read(), os.path.join(sys.path[0], 'framework.py'), 'exec'))

import unittest
TestRunner = unittest.TextTestRunner
suite = unittest.TestSuite()

tests = os.listdir(os.curdir)
tests = [n[:-3] for n in tests if n.startswith('test') and n.endswith('.py')]

for test in tests:
    m = __import__(test)
    if hasattr(m, 'test_suite'):
        suite.addTest(m.test_suite())

if __name__ == '__main__':
    TestRunner().run(suite)