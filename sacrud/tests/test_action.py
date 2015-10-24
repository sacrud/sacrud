from sacrud.action import CRUD

from .models import User


def table_fill(qty, model):
    def wrap(func):
        def wrapped(self, dbsession):
            users = [model(id=i + 1, name=i + 1) for i in range(qty)]
            dbsession.add_all(users)
            return func(self, dbsession)
        return wrapped
    return wrap


class TestRead(object):

    @table_fill(20, User)
    def test_read(self, dbsession):
        user = CRUD(dbsession, User).read().all()
        assert len(user) == 20

    @table_fill(20, User)
    def test_read_single(self, dbsession):
        user = CRUD(dbsession, User).read(5)
        assert user.id == 5

    @table_fill(20, User)
    def test_read_by_str_id(self, dbsession):
        user = CRUD(dbsession, User).read('5')
        assert user.id == 5

    @table_fill(20, User)
    def test_read_args(self, dbsession):
        users = CRUD(dbsession, User).read(1, '2', 3, 10, 20)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_of_tuple(self, dbsession):
        tuple_of_users = (1, 2, 3, 10, 20)
        users = CRUD(dbsession, User).read(tuple_of_users)
        assert [u.id for u in users] == list(tuple_of_users)

    @table_fill(20, User)
    def test_read_of_list(self, dbsession):
        list_of_users = [1, 2, 3, 10, 20]
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == list_of_users

    @table_fill(20, User)
    def test_read_json_of_list(self, dbsession):
        list_of_users = "[1, 2, 3, 10, 20]"
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_tuple_of_str(self, dbsession):
        tuple_of_users = ('1', '2', 3, '10', '20')
        users = CRUD(dbsession, User).read(tuple_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_list_of_str(self, dbsession):
        list_of_users = ['1', '2', '3', '10', '20']
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_json_list_of_str(self, dbsession):
        list_of_users = '["1", "2", "3", "10", "20"]'
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_by_dict_pk(self, dbsession):
        user = CRUD(dbsession, User).read({'id': 19})
        assert user.id == 19

    @table_fill(20, User)
    def test_read_json_by_dict_pk(self, dbsession):
        user = CRUD(dbsession, User).read('{"id": 19}')
        assert user.id == 19

    @table_fill(20, User)
    def test_read_list_of_dict(self, dbsession):
        list_of_users = [{'id': '1'}, {'id': '2'}, {'id': '3'},
                         {'id': 10}, {'id': 20}]
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_json_list_of_dict(self, dbsession):
        list_of_users = '''[{"id": "1"}, {"id": "2"}, {"id": "3"},
                            {"id": 10}, {"id": 20}]'''
        users = CRUD(dbsession, User).read(list_of_users)
        assert [u.id for u in users] == [1, 2, 3, 10, 20]

    @table_fill(20, User)
    def test_read_list_of_dict_and_then_delete(self, dbsession):
        list_of_users = [{'id': '1'}, {'id': '2'}, {'id': '3'},
                         {'id': 10}, {'id': 20}]
        CRUD(dbsession, User).read(list_of_users)\
            .delete(synchronize_session=False)
        rows = [item.id for item in CRUD(dbsession, User).read().all()]
        assert 1 not in rows
        assert 2 not in rows
        assert 3 not in rows
        assert 10 not in rows
        assert 20 not in rows
