

def before_insert(mapper, connection, target):

    cls = target.__class__
    position = target.position and target.position or 0

    connection.execute(cls.__table__.update().
                       values(position=cls.position + 1).
                       where(cls.id != target.id).
                       where(cls.position >= position)
                       )

