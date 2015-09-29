import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from sqlalchemy import and_
from mpp.models import Response


class Reader(object):
    def __init__(self, config):
        # set up the connection
        engine = sqla.create_engine(config.get('connection'))
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def read(self, query, limit=10, offset=0):
        pass


class ResponseReader(Reader):
    def _build_clauses(self, query):
        # TODO: care about this
        clauses = []
        return clauses

    def read(self, query, limit=10, offset=0):
        # clauses = self._build_clauses(query)
        # TODO: not hardcode the query, obviously
        clauses = [Response.format == 'xml']
        return self.session.query(Response).filter(and_(*clauses)).limit(limit).offset(offset).all()
