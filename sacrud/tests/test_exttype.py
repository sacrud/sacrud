#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
import uuid

import transaction
from sqlalchemy import Column, Integer

from sacrud.exttype import GUID
from sacrud.tests import Base, BaseSacrudTest


class ExtTypeModel(Base):
    __tablename__ = "exttypemodel"

    id = Column(Integer, primary_key=True)
    col_guid = Column(GUID(), default=uuid.uuid4)


class ExtTypeTest(BaseSacrudTest):

    def test_guid(self):
        guid = ExtTypeModel()
        value = uuid.uuid4()
        guid.col_guid = value
        self.session.add(guid)
        self.session.flush()
        self.assertEqual(guid.col_guid, value)

        value = '7a5e9335-424b-48fd-9426-b1a33d16ba3f'
        guid.col_guid = value
        self.session.add(guid)
        self.session.flush()
        self.assertEqual(guid.col_guid, value)
        transaction.commit()

        guid = self.session.query(ExtTypeModel).one()
        self.assertEqual(guid.col_guid, uuid.UUID(value))

        value = None
        guid.col_guid = value
        self.session.add(guid)
        self.session.flush()
        self.assertEqual(guid.col_guid, value)
        transaction.commit()

        guid = self.session.query(ExtTypeModel).one()
        self.assertEqual(guid.col_guid, value)
