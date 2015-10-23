from zope.sqlalchemy import ZopeTransactionExtension

import pytest
from sqlalchemy import orm, create_engine


def pytest_generate_tests(metafunc):
    if 'dbsession' in metafunc.fixturenames:
        metafunc.parametrize("dbsession", ['d1', 'd2'], indirect=True)


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


@pytest.fixture(scope="session")
def dbsession(request):
    from .models import User, Group, Good
    engine = create_engine('sqlite:///:memory:')
    for t in [User, Group, Good]:
        t.metadata.create_all(engine)
    if request.param == "d1":
        return sqlalchemy_session(engine)
    elif request.param == "d2":
        return zopetransaction_session(engine)
    else:
        raise ValueError("invalid internal test config")
