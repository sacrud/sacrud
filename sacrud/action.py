#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
CREATE, READ, DELETE, UPDATE actions for SQLAlchemy models
"""
import transaction
from marshmallow_sqlalchemy import ModelSchema

from .common import unjson, get_obj
from .exceptions import CreateDublicate


class CRUD(object):

    """ Main class for CRUD actions

        :Parameters:

            - `session`: SQLAlchemy DBSession
            - `table`: SQLAlchemy model
            - `commit`: To do or not after modify object
            - `preprocessing`: you custom preprocessing class
    """

    def __init__(self, session, table, model_schema=ModelSchema, commit=True):
        self.table = table
        self.session = session
        self.commit = commit
        if not hasattr(model_schema.Meta, 'model')\
                or not model_schema.Meta.model:
            class Schema(ModelSchema):
                class Meta:
                    model = self.table
            self.schema = Schema()
        else:
            self.schema = model_schema()
        self.schema.session = self.session

    def create(self, data, update=False, **kwargs):
        """
        Creates a new object pretreated input data.

        .. code-block:: python

            DBSession.sacrud(Users).create({'name': 'Vasya', 'sex': 1})

        Support JSON:

        .. code-block:: python

            DBSession.sacrud(Users).create('{"name": "Vasya", "sex": 1}')

        For adding multiple data for m2m or m2o use endinng `[]`, ex.:

        .. code-block:: python

            DBSession.sacrud(Users).create(
                {'name': 'Vasya', 'sex': 1,
                 'groups[]': ['["id", 1]', '["id", 2]']}
            )
        """
        data = unjson(data)
        if update is False:
            if self.schema.get_instance(unjson(data)):
                raise CreateDublicate
        instance = self.schema.load(data).data
        return self._add(instance, data, **kwargs)

    def read(self, *pk):
        """
        Return a list of entries in the table or single
        entry if there is an pk.

        .. code-block:: python

            # All users
            DBSession.sacrud(Users).read()

            # Composite primary_key
            DBSession.sacrud(User2Groups).read({'user_id': 4, 'group_id': 2})

            # Multiple rows
            primary_keys = [
                {'user_id': 4, 'group_id': 2},
                {'user_id': 4, 'group_id': 3},
                {'user_id': 1, 'group_id': 1},
                {'user_id': 19, 'group_id': 2}
            ]
            DBSession.sacrud(User2Groups).read(*primary_keys)

            # JSON using
            primary_keys = '''[
                {"user_id": 4, "group_id": 2},
                {"user_id": 4, "group_id": 3},
                {"user_id": 1, "group_id": 1},
                {"user_id": 19, "group_id": 2}
            ]'''
            DBSession.sacrud(User2Groups).read(primary_keys)

            # Delete
            DBSession.sacrud(User2Groups).read(*primary_keys)\
                .delete(synchronize_session=False)

            # Same, but work with only not composite primary key
            DBSession.sacrud(Users).read((5, 10))       # as list
            DBSession.sacrud(Users).read('[5, 10]')     # as JSON
            DBSession.sacrud(Users).read('{"id": 5}')   # as JSON explicit pk
            DBSession.sacrud(Users).read(5, "1", 2)     # as *args
            DBSession.sacrud(Users).read(42)            # single
        """
        pk = [unjson(obj) for obj in pk]

        if len(pk) == 1:  # like ([1,2,3,4,5], )
            return get_obj(self.session, self.table, pk[0])
        elif len(pk) > 1:  # like (1, 2, 3, 4, 5)
            return get_obj(self.session, self.table, pk)
        return self.session.query(self.table)

    def update(self, pk, data, **kwargs):
        """
        Updates the object by primary_key:

        .. code-block:: python

            DBSession.sacrud(Users).update(1, {'name': 'Petya'})
            DBSession.sacrud(Users).update('1', {'name': 'Petya'})
            DBSession.sacrud(User2Groups).update({'user_id': 4, 'group_id': 2},
                                                 {'group_id': 1})

        JSON support:

        .. code-block:: python

            DBSession.sacrud(Users).update(1, '{"name": "Petya"}')
            DBSession.sacrud(User2Groups).update(
                '{"user_id": 4, "group_id": 2}',    # primary_key
                '{"group_id": 1}'                   # data
            )

        Default it run ``session.commit() or transaction.commit()``.
        If it is not necessary use attribute ``commit=False``.
        """
        data = unjson(data)
        instance = self.schema.get_instance(unjson(pk))
        return self._add(
            self.schema.load(data, instance=instance).data,  # Instance
            data,
            **kwargs
        )

    def delete(self, pk, **kwargs):
        """
        Delete the object by primary_key:

        .. code-block:: python

            DBSession.sacrud(Users).delete(1)
            DBSession.sacrud(Users).delete('1')
            DBSession.sacrud(User2Groups).delete({'user_id': 4, 'group_id': 2})

        JSON support:

        .. code-block:: python

            DBSession.sacrud(User2Groups).delete(
                '{"user_id": 4, "group_id": 2}'
            )

        Default it run ``session.commit() or transaction.commit()``.
        If it is not necessary use attribute ``commit=False``.
        """
        pk = unjson(pk)
        instance = self.schema.get_instance(pk)
        self.session.delete(instance)
        self._commit(**kwargs)
        return {'pk': pk, 'name': instance.__repr__()}

    def _add(self, instance, data, **kwargs):
        """ Update the object directly.

        .. code-block:: python

            DBSession.sacrud(Users)._add(UserObj, {'name': 'Gennady'})
        """
        self.session.add(instance)
        self._commit(**kwargs)

        return instance

    def _commit(self, **kwargs):
        if kwargs.get('commit', self.commit) is True:
            try:
                self.session.commit()
            except AssertionError:
                transaction.commit()
