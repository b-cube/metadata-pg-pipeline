#!/anaconda/bin/python

import json
from mpp.loaders import Loader
from mpp.utils import validate_in_memory
from mpp.models import Validation, Response
from datetime import datetime
import traceback
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

from multiprocessing import Process, cpu_count, Manager
from Queue import Empty

# validating everything, including the federal stuff


def _partition()



def producer_queue(queue, ranges):
    for response_id, cleaned_content in read_session.query(Response.id, Response.cleaned_content).filter(
            and_(Response.schemas is not None, Response.schemas != '{}')).limit(ranges[0]).offset(ranges[1]).all():
        stderr = validate_in_memory(cleaned_content)
        validated_data =  {
            "response_id": response_id,
            "valid": 'Error at' not in stderr,
            "validated_on": datetime.now().isoformat()
        }
        if stderr:
            validated_data.update({
                "errors": [s.strip() for s in stderr.split('\n\n') if s]
            })
        queue.put(validated_data)
    queue.put('STOP')


def consumer_queue(proc_id, queue):
    loader = Loader(conf)
    while True:
        try:
            consumer_data = queue.get(proc_id, 1)
            if consumer_data == 'STOP':
                queue.put('STOP')
                break

            for data in consumer_data:
                v = Validation()
                v.create(data)
                loader.load(v)
        except Empty:
            pass
    loader.close()


class TheManager(object):
    def __init__(self, limit, offset):
        self.manager = Manager()
        self.queue = self.manager.Queue()
        self.NUMBER_OF_PROCESSES = cpu_count()
        self.limit = limit
        self.offset = 

    def start(self):
        self.producer - Process(
            target=producer_queue,
            args=(self.queue)
        )

if __name__ == '__main__':
    # set up the connection
    with open('local_rds.conf', 'r') as f:
        conf = json.loads(f.read())

    # loader = Loader(conf)

    # our connection
    read_engine = sqla.create_engine(conf.get('connection'))
    read_Session = sessionmaker()
    read_Session.configure(bind=read_engine)
    read_session = read_Session()

    LIMIT = 1000
    for i in xrange(0, 213045, LIMIT):
        print 'QUERYING {0}'.format(i)


read_session.close()
