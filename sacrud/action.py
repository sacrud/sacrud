# -*- coding: utf-8 -*-
import os
import ast
import uuid
import inspect
import sqlalchemy
import transaction

prefix = 'crud'


def get_pk(table):
    # FIXME: кривое исключение
    """ Return primary key name of table.

    :Parameters:
        - `table`: SQLAlchemy table.

    :Examples:

    >>> from sqlalchemy import Column, Integer
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> Base = declarative_base()
    >>> class User(Base):
    ...     __tablename__ = 'users'
    ...     id = Column(Integer, primary_key=True)
    >>> get_pk(User())
    'id'

    """
    try:
        pk = table.__mapper__.primary_key[0].name
    except:
        pk = ''

    return pk


def get_relations(obj):
    """
    :Examples:

    >>> from sqlalchemy import Column, Integer, ForeignKey
    >>> from sqlalchemy.ext.declarative import declarative_base
    >>> from sqlalchemy.orm import relationship, backref
    >>> Base = declarative_base()
    >>> class User(Base):
    ...    __tablename__ = 'users'
    ...    id = Column(Integer, primary_key=True)
    ...
    >>> class Address(Base):
    ...    __tablename__ = 'addresses'
    ...    id = Column(Integer, primary_key=True)
    ...    user_id = Column(Integer, ForeignKey('users.id'))
    ...    user = relationship("User", backref=backref('addresses', order_by=id))
    >>> get_relations(User())
    [('addresses', [])]

    """
    return [(n, getattr(obj, n)) for n in dir(obj)
            if isinstance(getattr(obj, n),
                          sqlalchemy.orm.collections.InstrumentedList)]


def index(session, table, order_by=None):
    """
    Return a list of table rows.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `order_by`: name ordered row.
    """
    col = [c for c in table.__table__.columns]
    pk_name = get_pk(table)
    query = session.query(table)
    if order_by:
        query = query.order_by(order_by)
    row = query.all()
    if hasattr(table, '__mapper_args__'):
        mapper_args = table.__mapper_args__
    else:
        mapper_args = {}

    return {'row': row,
            'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix,
            'mapper_args': mapper_args, }


def create(session, table, request=''):
    """
    Insert row to table.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `request`: webob format request.
    """
    if request:
        args = {}
        # FIXME: я чувствую здесь диссонанс
        for arg in inspect.getargspec(table.__init__).args[1:]:
            args[arg] = None
        obj = table(**args)
        for key, value in request.items():
            # chek columns exist
            if not key in table.__table__.columns:
                continue
            value = check_type(request, table, key)
            obj.__setattr__(key, value)
        session.add(obj)
        transaction.commit()
        return

    pk_name = get_pk(table)
    col = [c for c in table.__table__.columns]
    return {'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix}


def read(session, table, pk):
    """
    Select row by pk.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `pk`: primary key value.
    """
    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    col = [c for c in table.__table__.columns]
    return {'obj': obj,
            'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix,
            'rel': get_relations(obj)}


def update(session, table, pk, request=''):
    """
    Update row of table.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `request`: webob format request.
    """

    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    col_list = [c for c in table.__table__.columns]

    if request:
        for col in col_list:
            if col.name not in request:
                continue
            if getattr(obj, col.name) == request[col.name][0]:
                continue
            if col.type.__class__.__name__ == 'FileStore':
                if not hasattr(request[col.name][0], 'filename'):
                    continue
            value = check_type(request, table, col.name, obj)
            setattr(obj, col.name, value)
        session.add(obj)
        transaction.commit()
        return

    return {'obj': obj,
            'pk': pk_name,
            'col': col_list,
            'table': table,
            'prefix': prefix}


def delete(session, table, pk):
    """
    Delete row by pk.

    :Parameters:

        - `session`: DBSession.
        - `table`: table instance.
        - `pk`: primary key value.
    """

    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    check_type('', table, obj=obj)
    session.delete(obj)
    transaction.commit()


def delete_fileobj(table, obj, key):
    """ Delete atached file.
    """
    abspath = table.__table__.columns[key].type.abspath
    path = os.path.join(abspath, os.path.basename(getattr(obj, key)))
    if not obj or not os.path.isfile(path):
        return
    os.remove(path)


def check_type(request, table, key=None, obj=None):
    """ Chek type when Create, Update or Delete.
    """

    # for Delete
    if not key:
        for col in table.__table__.columns:
            if col.type.__class__.__name__ == 'FileStore':
                if getattr(obj, col.name):
                    delete_fileobj(table, obj, col.name)
        return
    column_type = table.__table__.columns[key].type.__class__.__name__

    # for Update or Create
    value = request[key]
    if type(value) in (list, tuple):
        value = value[0]
    if column_type == 'Boolean':
        value = False if value == '0' else True
        value = True if value else False
    elif column_type == 'FileStore':
        if request[key] is None:
            return None
        fileobj = request[key][0]
        if hasattr(fileobj, 'filename'):
            extension = fileobj.filename.split(".")[-1]
            fileobj.filename = str(uuid.uuid4()) + "." + extension
            abspath = table.__table__.columns[key].type.abspath
            store_file(request, key, abspath)
            if obj:
                if getattr(obj, key):
                    delete_fileobj(table, obj, key)
            value = fileobj.filename
    elif column_type == 'HSTORE':
        value = ast.literal_eval(value)
    return value


def store_file(request, key, path):
    """ Load atached file.
    """
    # ``filename`` contains the name of the file in string format.
    #
    # WARNING: this example does not deal with the fact that IE sends an
    # absolute file *path* as the filename.  This example is naive; it
    # trusts user input.
    filename = request[key][0].filename

    # ``input_file`` contains the actual file data which needs to be
    # stored somewhere.

    input_file = request[key][0].file

    # Using the filename like this without cleaning it is very
    # insecure so please keep that in mind when writing your own
    # file handlingself.
    file_path = os.path.join(path, filename)
    output_file = open(file_path, 'wb')

    # Finally write the data to the output file
    input_file.seek(0)
    while 1:
        data = input_file.read(2 << 16)
        if not data:
            break
        output_file.write(data)
    output_file.close()
