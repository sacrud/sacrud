# -*- coding: utf-8 -*-
import os
import ast
import inspect
import datetime
import calendar
import sqlalchemy
import transaction

prefix = 'crud'


def get_pk(table):
    # FIXME: кривое исключение
    try:
        pk = table.__mapper__.primary_key[0].name
    except:
        pk = 'all'

    return pk


def get_relations(obj):
    return [(n, getattr(obj, n)) for n in dir(obj)
            if isinstance(getattr(obj, n),
            sqlalchemy.orm.collections.InstrumentedList)]


def index(session, table):
    """
    Return row list of table
    """
    col = [c for c in table.__table__.columns]
    pk_name = get_pk(table)
    row = session.query(table).all()
    return {'row': row,
            'pk': pk_name,
            'col': col,
            'table': table,
            'prefix': prefix}


def create(session, table, request=''):
    """docstring for create"""
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
    """docstring for red"""
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
    """docstring for read"""
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
    """docstring for delete"""
    pk_name = get_pk(table)
    obj = session.query(table).filter(getattr(table, pk_name) == pk).one()
    check_type('', table, obj=obj)
    session.delete(obj)
    transaction.commit()


def delete_fileobj(table, obj, key):
    abspath = table.__table__.columns[key].type.abspath
    if not obj:
        return
    os.remove(os.path.join(abspath, os.path.basename(getattr(obj, key))))


def check_type(request, table, key=None, obj=None):
    # chek type when Create, Update or Delete

    # for Delete
    if not key:
        for col in table.__table__.columns:
            if col.type.__class__.__name__ == 'FileStore':
                if getattr(obj, col.name):
                    delete_fileobj(table, obj, col.name)
        return
    column_type = table.__table__.columns[key].\
                        type.__class__.__name__
    # for Update or Create

    value = request[key]
    # Заменяет пустые строки на None
    if value[0] == '':
        value[0] = None
    if column_type == 'Boolean':
        value[0] = False if value[0] == '0' else True
    elif column_type == 'FileStore':
        if request[key][0] is None:
            return None
        request[key][0].filename = str(calendar.timegm(datetime.
                datetime.now().utctimetuple())) +\
                request[key][0].filename
        abspath = table.__table__.columns[key].type.abspath
        store_file(request, key, abspath)
        if obj:
            if getattr(obj, key):
                delete_fileobj(table, obj, key)
        value[0] = request[key][0].filename
    elif column_type == 'HSTORE':
        value[0] = ast.literal_eval(value[0])

    return value[0]


def store_file(request, key, path):
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
