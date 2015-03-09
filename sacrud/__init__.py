#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

import types

from .action import CRUD

__all__ = ['crud_sessionmaker', ]


def crud_sessionmaker(session):
    """
    Wraps SQLAlchemy session adding there ``sacrud`` method.

    ::

        from sqlalchemy.orm import scoped_session, sessionmaker
        from sacrud import crud_sessionmaker

        DBSession = crud_sessionmaker(scoped_session(sessionmaker()))
        help(DBSession.sacrud)
    """
    session.sacrud = types.MethodType(CRUD, session)
    return session
