#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
import os
import uuid
from io import StringIO

import transaction
from sqlalchemy import Column, Integer

from sacrud.exttype import GUID, ChoiceType, SlugType
from sacrud.tests import (Base, BaseSQLAlchemyTest, BaseZopeTest, FileStore,
                          MockCGIFieldStorage, Profile, User)

file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
TEST_CHOICES = {'val_1': 'val_1', 'val_2': 'val_2', 'val_3': 'val_3',
                'val_4': 'val_4', 'val_5': 'val_5', 'val_6': 'val_6'}


class ExtTypeModel(Base):
    __tablename__ = "exttypemodel"

    id = Column(Integer, primary_key=True)
    col_guid = Column(GUID(), default=uuid.uuid4)
    col_choice = Column(ChoiceType(choices=TEST_CHOICES.items()),
                        info={"verbose_name": u'Проверка select', })
    slug = Column(SlugType('string_name', False))


class ExtTypeTest(object):

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
        self.assertEqual(str(guid.col_guid), str(uuid.UUID(value)))

        value = None
        guid.col_guid = value
        self.session.add(guid)
        self.session.flush()
        self.assertEqual(guid.col_guid, value)
        transaction.commit()

        guid = self.session.query(ExtTypeModel).one()
        self.assertEqual(guid.col_guid, value)

    def test_file_storage(self):

        user = User(u'Vasya', u'Pupkin', u"123")
        self.session.add(user)
        transaction.commit()

        request = {}
        request['user_id'] = 1
        request['phone'] = 213123123
        request['cv'] = "Vasya Pupkin was born in Moscow"
        request['married'] = True
        request["salary"] = 23.0

        upload = MockCGIFieldStorage()
        upload.file = StringIO(u'foo')
        upload.filename = 'foo.html'
        request["photo"] = upload

        profile = Profile(**request)
        self.session.add(profile)
        transaction.commit()

        profile = self.session.query(Profile).get(1)
        if hasattr(profile.photo, 'filename'):
            self.assertEqual(profile.photo.filename, 'foo.html')
        else:
            self.assertEqual(profile.photo, '/assets/photo/foo.html')

        # test URL
        request["photo"] = 'https://www.linux.org.ru/img/good-penguin.jpg'

        profile = Profile(**request)
        self.session.add(profile)
        transaction.commit()

        profile = self.session.query(Profile).order_by('-id').first()
        self.assertEqual(profile.photo,
                         'https://www.linux.org.ru/img/good-penguin.jpg')

        # test repr
        self.assertEqual(FileStore().__repr__(), '')
        self.assertEqual(FileStore(path="/foo/bar/").__repr__(), '/foo/bar/')

    def test_choices_type(self):
        obj = ExtTypeModel()
        value = 'val_5'
        obj.col_choice = value
        self.session.add(obj)
        self.session.flush()
        self.assertEqual(obj.col_choice, value)

        transaction.commit()

        obj = self.session.query(ExtTypeModel).one()
        self.assertEqual(obj.col_choice, 'val_5')

    def test_slug_type(self):
        obj = ExtTypeModel()
        value = 'test'
        obj.slug = value
        self.session.add(obj)
        self.session.flush()
        self.assertEqual(obj.slug, value)

        transaction.commit()

        obj = self.session.query(ExtTypeModel).one()
        self.assertEqual(obj.slug, value)


class ZopeTransaction(BaseZopeTest, ExtTypeTest):
    pass


class SQLAlchemyTransaction(BaseSQLAlchemyTest, ExtTypeTest):
    pass
