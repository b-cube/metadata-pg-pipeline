import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import Table, MetaData, Column, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import relationship, backref
# from sqlalchemy.ext.declarative import declarative_base


metadata = sqla.MetaData()
# Base = declarative_base()


responses_table = Table(
    'responses',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('source_url_sha', String(100)),
    Column('source_url', String),
    Column('xml_content_as_str', TEXT),
    Column('initial_harvest_date', DateTime),
    Column('raw_content', String),
    Column('raw_content_md5', String),
    Column('inlinks', ARRAY(String)),
    Column('outlinks', ARRAY(String)),
    Column('host', String),
    Column('headers', ARRAY(String))
)


class Response(object):
    def __init__(self, sha_id):
        self.source_url_sha = sha_id

validations_table = Table(
    'validations',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('validated_on', DateTime),
    Column('errors', ARRAY(String)),
    Column('valid', Boolean),
    Column('response_id', Integer)
)


mapper(Response, responses_table)
