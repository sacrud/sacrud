import unittest
from pyramid import testing

class TestCreate(unittest.TestCase):

    def _makeRequest(self):
        request = testing.DummyRequest()
        request.registry._zodb_databases = {'':DummyDB()}
        return request
    
    def test_test(self):
        raise Exception(123)
