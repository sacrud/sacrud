#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

import types

from sqlalchemy.orm import Session

from .action import CRUD

__all__ = ['crud_sessionmaker', 'CRUDSession']


class CRUDSession(Session):
    """
    Wraps SQLAlchemy session adding there ``sacrud`` method.

    ::

        from sqlalchemy.orm import scoped_session, sessionmaker
        from sacrud import CRUDSession

        Session = scoped_session(sessionmaker(class_=CRUDSession))
        session = Session()
        DBSession.sacrud(User).delete(1)
    """
    def sacrud(self, cls, *args, **kwargs):
        return CRUD(self, cls, *args, **kwargs)


def crud_sessionmaker(session):
    """
    Wraps zope.sqlalchemy session adding there ``sacrud`` method.

    ::

        from sqlalchemy.orm import scoped_session, sessionmaker
        from zope.sqlalchemy import ZopeTransactionExtension
        from sacrud import crud_sessionmaker

        DBSession = crud_sessionmaker(scoped_session(
            sessionmaker(extension=ZopeTransactionExtension())))
        DBSession.sacrud(User).delete(1)
    """
    session.sacrud = types.MethodType(CRUD, session)
    return session
