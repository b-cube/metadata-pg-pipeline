import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import Table, MetaData, Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import *


metadata = Metadata()


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


mapper(Response, response_table)


class Response(object):
    def __init__(self, sha_id):
        self.source_url_sha = sha_id
