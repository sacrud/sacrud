#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Extension type for SQLAlchemy
"""
import os
import uuid

from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.types import CHAR, String, TypeDecorator, Unicode, VARCHAR


class FileStore(TypeDecorator):
    impl = VARCHAR

    def __init__(self, path='', abspath='', *arg, **kw):
        TypeDecorator.__init__(self, *arg, **kw)
        self.path = path
        self.abspath = abspath

    def process_bind_param(self, value, dialect):
        if value is not None:
            if hasattr(value, 'filename'):
                return os.path.join(self.path, value.filename)
            if 'http://' in value or 'https://' in value:
                return value
            return os.path.join(self.path, value)

    def process_result_value(self, value, dialect):
        if value is not None:
            value = value
        return value

    def __repr__(self):
        return self.path


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())  # pragma: no cover
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)  # pragma: no cover
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class ElfinderString(TypeDecorator):
    impl = Unicode

    def __init__(self, *arg, **kw):
        TypeDecorator.__init__(self, *arg, **kw)

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value


class ChoiceType(TypeDecorator):
    """ Example:

.. code-block:: python
    :linenos:

    from sacrud.exttype import ChoiceType

    Base = declarative_base()

    REDIRECT_CHOICES = (
        ('OK (200)', '200'),
        ('Moved Permanently (301)', '301'),
        ('Moved Temporarily (302)', '302'),
    )

    class SuperChoiceModel(Base):
        ...
        redirect_type = Column(ChoiceType(choices=REDIRECT_CHOICES))
    """

    impl = String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        val = [(k, v) for k, v in self.choices.iteritems() if k == value or v == value]
        if val:
            return val[0][1]
        return None

    def process_result_value(self, value, dialect):
        if not value:
            return None
        choices = {v: k for k, v in self.choices.items()}
        return (value, choices[value])


class SlugType(TypeDecorator):

    impl = String

    def __init__(self, input_id, reflection=True, **kw):
        self.input_id = input_id
        self.reflection = reflection
        super(SlugType, self).__init__(**kw)
