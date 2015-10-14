#!/anaconda/bin/python

import json as js
import urlparse
import traceback

import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    MetaData,
    Column,
    String,
    Integer
)
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class XmlJson(Base):
    __tablename__ = 'xml_with_jsons'
    id = Column(Integer, primary_key=True)
    file = Column(String)
    extracted_json = Column(JSON)
    xpath = Column(String)
    host = Column(String)
    def __repr__(self):
        return 'XmlJson ({0} {1})'.format(self.file, self.host)


with open('big_rds.conf', 'r') as f:
    conf = js.loads(f.read())
engine = sqla.create_engine(conf.get('connection'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

with open('../../Response-Identification-Info/notebooks/outputs/responses_with_json.csv', 'r') as f:
    lines = f.readlines()

for line in lines[1:]:
    parts = line.strip().split('|')
    filepath = parts[0].split('/')[-1].replace('.json', '')
    j = js.loads(parts[1])
    xpath = parts[2]

    with open(parts[0].strip(), 'r') as f:
        data = js.loads(f.read())
    url = data.get('url')
    host = urlparse.urlparse(url).netloc

    xj = XmlJson()
    xj.file=filepath
    xj.extracted_json=j
    xj.xpath=xpath
    xj.host=host

    try:
        session.add(xj)
        session.commit()
        session.flush()
    except Exception as ex:
        print xj
        session.rollback()
        traceback.print_exc()
