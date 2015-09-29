import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.exc import IntegrityError
from mpp.models import Response
from semproc.rawresponse import RawResponse
from semproc.parser import Parser
from semproc.xml_utils import extract_attribs
from lxml import etree
import traceback


class Loader(object):
    def __init__(self, config):
        # set up the connection
        engine = sqla.create_engine(config.get('connection'))
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

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
        # TODO: this might not split everything successfully
        return [a.strip() for s in schemas for a in s.split() if s] if schemas else []

    def load(self, doc):
        '''
        doc here is the solr doc with
        potentially a few additional keys for
        things like schemas (can be from pipeline
        processing or injected from somewhere else)
        '''

        # the sha (generated from url if not in doc)
        response = Response()
        response.source_url_sha = doc.get('url_hash')
        # TODO: verify that the pipeline output contains this
        response.source_url = doc.get('url')
        # this should come from the cleaned output of
        # the pipeline so that we don't need to keep
        # dealing with really junky strings
        # TODO: switch to pipeline clean content
        cleaned_content = self._clean(doc.get('raw_content', ''))

        try:
            parser = Parser(cleaned_content)
            cleaned_content = etree.tostring(parser.xml, pretty_print=True)
            fmt = 'xml'
        except Exception as ex:
            print 'xml error', ex
            try:
                clean_json = json.loads(cleaned_content)
                fmt = 'json'
            except:
                fmt = 'unknown'

        try:
            response.namespaces = parser.namespaces.items()
        except Exception as ex:
            print 'namespace error', ex

        try:
            response.schemas = self._pull_schemas(parser.xml)
        except Exception as ex:
            print 'schema error', ex
            traceback.print_exc()

        response.format = fmt
        response.cleaned_content = cleaned_content

        response.raw_content = doc.get('raw_content', '')
        response.raw_content_md5 = doc.get('digest', '')
        response.initial_harvest_date = doc.get('tstamp')
        response.host = doc.get('host', '')
        response.inlinks = doc.get('inlinks', [])
        response.outlinks = doc.get('outlinks', [])
        response.headers = doc.get('response_headers', [])

        try:
            self.session.add(response)
            self.session.commit()
            self.session.flush()

        except IntegrityError:
            self.session.rollback()
        except Exception as ex:
            print ex
            self.session.rollback()
