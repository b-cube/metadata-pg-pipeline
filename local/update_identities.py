import json as js
import os
from mpp.models import Identity
# from sqlalchemy.exc import IntegrityError
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker

'''
add the additional identities

last id before import: 55497
'''

sql = """
select r.id, r.source_url_sha
from responses r
where not exists(
    select i.response_id
    from identities i
    where r.id = i.response_id
) and format = 'xml'
limit %s
offset %s;
"""


with open('big_rds.conf', 'r') as f:
    conf = js.loads(f.read())

# our connection
engine = sqla.create_engine(conf.get('connection'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

start = 0
end = 556900
limit = 1000
for i in xrange(start, end, limit):
    for response_id, response_sha in session.execute(sql % (limit, i)):
        fname = '/home/ubuntu/semantics_pipeline/pipeline_tests/identified/%s_identified.json' % response_sha
        if not os.path.exists(fname):
            continue

        with open(fname, 'r') as f:
            data = js.loads(f.read())

        identity = data.get('identity', [])
        if identity:
            try:
                d = Identity(
                    identity=identity,
                    response_id=response_id
                )
                session.add(d)
                session.commit()
            except:
                session.rollback()
