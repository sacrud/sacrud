from sqlalchemy import (
    Text,
    Float,
    Column,
    String,
    Boolean,
    Integer,
    ForeignKey
)
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DBSession = scoped_session(sessionmaker())


class Group2User(Base):
    __tablename__ = 'group2user'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    groups = relationship("Group", secondary="group2user", backref="users")

    def __repr__(self):
        return self.name


class Profile(Base):

    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship(User, backref=backref("profile", lazy="joined"))
    phone = Column(String)
    cv = Column(Text)
    married = Column(Boolean)
    salary = Column(Float)


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))

    def __repr__(self):
        return self.name


class Good(Base):
    __tablename__ = 'goods'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship('Group', backref='goods')

    visible = Column(Boolean, default=False)
    archive = Column(Boolean)

    def __repr__(self):
        return self.name
