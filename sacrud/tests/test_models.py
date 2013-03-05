from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String, Text, Boolean, Float
from sqlalchemy.orm import relationship, backref
from sacrud.exttype import FileStore
import os

Base = declarative_base()

DIRNAME = os.path.dirname(__file__)
PHOTO_PATH = os.path.join(DIRNAME)


class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name,
                                            self.fullname,
                                            self.password)


class Profile(Base):

    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship(User, backref=backref("profile", lazy="joined"))
    phone = Column(String)
    cv = Column(Text)
    married = Column(Boolean)
    salary = Column(Float)
    photo = Column(FileStore(path="/assets/photo", abspath=PHOTO_PATH))

    def __init__(self, user, phone="", cv="", married=False, salary=20.0):
        self.user = user
        self.phone = phone
        self.cv = cv
        self.married = married
        self.salary = salary

    def __repr__(self):
        return "<Profile of user '%s'" % ((self.user, ))

    def set_photo(self, value):
        self.photo = value