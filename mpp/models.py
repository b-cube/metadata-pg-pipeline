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
from semproc.rawresponse import RawResponse
from semproc.parser import Parser
from semproc.xml_utils import extract_attribs
from lxml import etree
import traceback


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
    identities = relationship('Identity', backref='response')
    bags_of_words = relationship('BagOfWords', backref='response')

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
            docinfo = xml.docinfo
            sys_url = docinfo.system_url
            if sys_url:
                schemas.append(sys_url)
        except:
            pass

        # TODO: this might not split everything successfully
        return [
            a.strip() for s in schemas for a in s.split() if s
        ] if schemas else []

    def create(self, doc):
        # the sha (generated from url if not in doc)
        self.source_url_sha = doc.get('url_hash')
        # TODO: verify that the pipeline output contains this
        self.source_url = doc.get('url')
        # this should come from the cleaned output of
        # the pipeline so that we don't need to keep
        # dealing with really junky strings
        # TODO: switch to pipeline clean content

        # cleaned_content = self._clean(doc.get('raw_content', ''))

        # try:
        #     parser = Parser(cleaned_content)
        #     cleaned_content = etree.tostring(parser.xml, pretty_print=True)
        #     fmt = 'xml'
        # except Exception as ex:
        #     print 'xml error', ex
        #     try:
        #         clean_json = json.loads(cleaned_content)
        #         fmt = 'json'
        #     except:
        #         fmt = 'unknown'

        fmt = doc.get('response_datatype', 'unknown')
        cleaned_content = doc.get('content')

        if fmt == 'xml':
            parser = Parser(cleaned_content.encode('utf-8'))
            try:
                self.namespaces = parser.namespaces
            except Exception as ex:
                print 'namespace error', ex

            try:
                self.schemas = self._pull_schemas(parser.xml)
            except Exception as ex:
                print 'schema error', ex
                traceback.print_exc()

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
            (
                k.strip(), v.strip()) for k, v in
                    (h.split(':', 1) for h in headers)
        )


class Validation(Base):
    __tablename__ = 'validations'
    id = Column(Integer, primary_key=True)
    validated_on = Column(DateTime)
    errors = Column(ARRAY(String))
    valid = Column(Boolean)
    response_id = Column(Integer, ForeignKey('responses.id'))

    def create(self, doc):
        self.response_id = doc.get('response_id')
        self.valid = doc.get('valid')
        self.errors = doc.get('errors')
        self.validated_on = doc.get('validated_on')


class Identity(Base):
    __tablename__ = 'identities'
    id = Column(Integer, primary_key=True)
    identity = Column(JSON)
    response_id = Column(Integer, ForeignKey('responses.id'))

    def create(self, doc):
        self.response_id = doc.get('response_id')
        self.identity = doc.get('identity')


class BagOfWords(Base):
    __tablename__ = 'bag_of_words'
    id = Column(Integer, primary_key=True)
    generated_on = Column(DateTime)
    bag_of_words = Column(ARRAY(String))
    method = Column(String)
    response_id = Column(Integer, ForeignKey('responses.id'))

    def create(self, doc):
        self.response_id = doc.get('response_id')
        self.bag_of_words = doc.get('bag')
        self.method = doc.get('method')
        self.generated_on = doc.get('generated_on')
