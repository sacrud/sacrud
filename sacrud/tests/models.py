from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
DBSession = scoped_session(sessionmaker())


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))

    def __repr__(self):
        return self.name


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
