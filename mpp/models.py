import sqlalchemy as sqla
from sqlalchemy import (
    MetaData,
    Column,
    String,
    DateTime,
    Integer,
    Boolean,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    source_url_sha = Column(String(100))
    source_url = Column(String)
    cleaned_content = Column(TEXT)
    initial_harvest_date = Column(DateTime)
    raw_content = Column(String)
    raw_content_md5 = Column(String)
    inlinks = Column(ARRAY(String))
    outlinks = Column(ARRAY(String))
    host = Column(String)
    headers = Column(JSON)
    schemas = Column(ARRAY(String))
    namespaces = Column(JSON)
    format = Column(String(20))

    validations = relationship('Validation', backref='response')


class Validation(Base):
    __tablename__ = 'validations'
    id = Column(Integer, primary_key=True)
    validated_on = Column(DateTime)
    errors = Column(ARRAY(String))
    valid = Column(Boolean)
    response_id = Column(Integer, ForeignKey('responses.id'))
