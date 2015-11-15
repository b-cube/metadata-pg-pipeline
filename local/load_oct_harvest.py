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
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from semproc.rawresponse import RawResponse
from semproc.parser import Parser
from semproc.xml_utils import extract_attribs, extract_item
from lxml import etree
from datetime import datetime
import dateutil.parser as dateparser
import psycopg2

import traceback
import glob
import json as js

import warnings
warnings.filterwarnings('ignore')


Base = declarative_base()


def _convert_date(datestr):
    # convert the 4-8 char to an iso date and deal with unknowns
    if datestr.lower() in ['unknown', 'none']:
        return ''

    year = datestr[:4]
    month = datestr[4:6] if len(datestr) > 4 else '1'
    day = datestr[6:] if len(datestr) > 6 else '1'
    try:
        d = datetime(int(year), int(month), int(day))
        return d.isoformat()
    except:
        return ''


class Oct(Base):
    __tablename__ = 'oct_responses'
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
    metadata_age = Column(DateTime)
    response_identity = Column(JSON)

    def _clean(self, raw_content):
        # intermediate option if not running
        # from a pipeline output. temporary.
        rr = RawResponse('', raw_content, '')
        return rr.clean_raw_content()

    def _pull_schemas(self, xml):
        xpaths = [
            ['//*', '@schemaLocation'],
            ['//*', '@noNamespaceSchemaLocation']
        ]
        schemas = []
        for xp in xpaths:
            schemas += extract_attribs(xml, xp)

        # and, for older fgdc, try to get the dtd
        try:
            docinfo = xml.getroottree().docinfo
            sys_url = docinfo.system_url
            if sys_url:
                schemas.append(sys_url)
        except:
            pass

        # TODO: this might not split everything successfully
        return [
            a.strip() for s in schemas for a in s.split() if s
        ] if schemas else []

    def _extract_age(self, protocol, xml):
        if protocol == 'ISO':
            md_dates = extract_item(xml, ['//*', 'dateStamp', 'Date'])
            try:
                # this will use the current month, day
                # if only the year is provided (that isn't
                # valid iso anyway but i am not fixing it here)
                md_dates = dateparser.parse(md_dates)
            except:
                return None
        elif protocol == 'FGDC':
            md_date = extract_item(xml, ['//*', 'metainfo', 'metd'])
            try:
                md_dates = _convert_date(md_date)
            except:
                md_dates = None
        else:
            return None
        return md_dates

    def create(self, doc):
        # the sha (generated from url if not in doc)
        self.source_url_sha = doc.get('url_hash')
        # TODO: verify that the pipeline output contains this
        self.source_url = doc.get('url')
        fmt = doc.get('response_datatype', 'unknown')
        cleaned_content = doc.get('content')

        if fmt == 'xml':
            parser = Parser(cleaned_content.encode('utf-8'))

            if parser.xml is None:
                print self.source_url_sha, self.source_url
                fmt = 'xml;unparsed'

        #     try:
        #         self.namespaces = parser.namespaces
        #     except Exception as ex:
        #         print 'namespace error', ex

        #     try:
        #         self.schemas = self._pull_schemas(parser.xml)
        #     except Exception as ex:
        #         print 'schema error', ex
        #         traceback.print_exc()

        self.format = fmt
        self.cleaned_content = cleaned_content

        self.raw_content = doc.get('raw_content', '')
        self.raw_content_md5 = doc.get('digest', '')
        self.initial_harvest_date = doc.get('tstamp')
        self.host = doc.get('host', '')
        self.inlinks = doc.get('inlinks', [])
        self.outlinks = doc.get('outlinks', [])
        headers = doc.get('response_headers', [])
        self.headers = dict(
            (k.strip(), v.strip()) for k, v in (h.split(':', 1) for h in headers)
        )
        self.response_identity = next(iter(doc.get('identity', [])), {})

        # protocol = self.response_identity.get('protocol', '')
        # if protocol in ['ISO', 'FGDC']:
        #     age = self._extract_age(protocol, parser.xml)
        #     if age:
        #         self.metadata_age = age


# grab the clean text from the rds
with open('big_rds.conf', 'r') as f:
    conf = js.loads(f.read())

# our connection
engine = sqla.create_engine(conf.get('connection'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

files = glob.glob('../../semantics_pipeline/pipeline_tests/identified/*.json')
for f in files:
    with open(f, 'r') as g:
        data = js.loads(g.read())

    october = Oct()
    october.create(data)

    try:
        session.add(october)
        session.commit()
    except IntegrityError:
        continue
    except psycopg2.IntegrityError:
        continue
    except Exception as ex:
        print 'commit fail', f
        print ex
        print
        print
        session.rollback()

session.close()
