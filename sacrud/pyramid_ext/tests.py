import unittest
from pyramid import testing

class TestCreate(unittest.TestCase):

    def _makeRequest(self):
        request = testing.DummyRequest()
        return request
    
    def test_test(self):
        raise Exception(123)
