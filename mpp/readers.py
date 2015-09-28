import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from mpp.models import Response


class Reader(object):
    def __init__(self, config):
        # set up the connection
        engine = sqla.create_engine(config.get('connection'))
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def read(self, query):
        pass


class ResponseReader(Reader):
    def _build_clauses(self, query):
        clauses = []

        return clauses

    def read(self, query):
        clauses = self._build_clauses(query)
        self.session.query(Response).filter(*clauses)
