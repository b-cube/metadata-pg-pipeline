import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from sqlalchemy.exc import IntegrityError


class Loader(object):
    def __init__(self, config):
        # set up the connection
        engine = sqla.create_engine(config.get('connection'))
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.session = Session()

    def load(self, obj):
        '''
        some obj (Response, Validation, etc)
        '''
        try:
            self.session.add(obj)
            self.session.commit()
            self.session.flush()

        except IntegrityError:
            self.session.rollback()
        except Exception as ex:
            print ex
            self.session.rollback()
