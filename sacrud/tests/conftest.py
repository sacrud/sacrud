from zope.sqlalchemy import ZopeTransactionExtension

import pytest
from sqlalchemy import orm, create_engine

from .models import Good, User, Group, Profile, Group2User


def pytest_generate_tests(metafunc):
    if 'dbsession' in metafunc.fixturenames:
        metafunc.parametrize("dbsession", ['reqsa', 'reqzope'], indirect=True)


def sqlalchemy_session(engine):
    session = orm.scoped_session(orm.sessionmaker())
    session.configure(bind=engine)
    return session


def zopetransaction_session(engine):
    session = orm.scoped_session(
        orm.sessionmaker(
            extension=ZopeTransactionExtension(),
            expire_on_commit=False
        )
    )
    session.configure(bind=engine)
    return session


@pytest.fixture(scope="function")
def dbsession(request):
    engine = create_engine('sqlite:///:memory:')

    for t in [User, Group, Good, Group2User, Profile]:
        t.metadata.create_all(engine)
    if request.param == "reqsa":
        return sqlalchemy_session(engine)
    elif request.param == "reqzope":
        return zopetransaction_session(engine)
    else:
        raise ValueError("invalid internal test config")


@pytest.fixture(scope="function")
def transaction(request, dbsession):
    request_param = request.keywords.keys()  # XXX:
    if "reqsa" in request_param:
        dbsession.abort = dbsession.rollback
        return dbsession
    elif "reqzope" in request_param:
        import transaction
        transaction.rollback = transaction.abort
        return transaction


@pytest.fixture(scope="function")
def request_data(request):
    return {}


@pytest.fixture(scope="function")
def init_users(dbsession):
    users = [User(id=i + 1, name=i + 1) for i in range(20)]
    dbsession.add_all(users)


@pytest.fixture(scope="function")
def init_groups(dbsession):
    groups = [Group(id=i + 1, name=i + 1) for i in range(20)]
    dbsession.add_all(groups)
