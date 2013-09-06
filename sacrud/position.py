def before_insert(mapper, connection, target):

    cls = target.__class__
    pos_name = target.__mapper_args__['order_by']
    pos_field = target.__getattribute__(pos_name)
    position = pos_field and pos_field or 0

    connection.execute(cls.__table__.
                       update(values={pos_name: getattr(cls, pos_name) + 1}).
                       where(cls.id != target.id).
                       where(getattr(cls, pos_name) >= position)
                       )
