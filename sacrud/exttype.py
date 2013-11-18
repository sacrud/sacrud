import os
from sqlalchemy.types import TypeDecorator, VARCHAR


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
