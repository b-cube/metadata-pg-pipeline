import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.exc import IntegrityError
from models import Response


class Loader(object):
    def __init__(self, config):
        # set up the connection
        engine = sqla.create_engine(config.get('connection'))
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def load(self, doc):
        response = Response('')
        response.source_url = source_url
        # this should come from the cleaned output of
        # the pipeline so that we don't need to keep
        # dealing with really junky strings
        response.xml_content_as_str = etree.tostring(xml, pretty_print=True)
        response.raw_content = raw_content
        response.raw_content_md5 = digest
        response.initial_harvest_date = tstamp
        response.host = host
        response.inlinks = inlinks
        response.outlinks = outlinks
        response.headers = headers

        try:
            self.session.add(response)
            self.session.commit()
            self.session.flush()

        except IntegrityError:
            self.session.rollback()
        except Exception as ex:
            print ex
            self.session.rollback()
