from sacrud.action import CRUD

from .models import User


def table_fill(qty, model):
    def wrap(func):
        def wrapped(self, dbsession):
            users = [model(id=i, name=i) for i in range(qty)]
            dbsession.add_all(users)
            return func(self, dbsession)
        return wrapped
    return wrap


class TestRead(object):

    @table_fill(20, User)
    def test_read(self, dbsession):
        user = CRUD(dbsession, User).read().all()
        assert len(user) == 20
