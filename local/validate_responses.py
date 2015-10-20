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

# validating everything, including the federal stuff
with open('validation_logs.log', 'w') as f:
    f.write('validating {0}\n'.format(datetime.now().isoformat()))

# set up the connection
with open('local_rds.conf', 'r') as f:
    conf = json.loads(f.read())

loader = Loader(conf)

# our connection
read_engine = sqla.create_engine(conf.get('connection'))
read_Session = sessionmaker()
read_Session.configure(bind=read_engine)
read_session = read_Session()

LIMIT = 1000
for i in xrange(0, 213045, LIMIT):
    for response in read_session.query(Response).filter(
            and_(Response.schemas is not None, Response.schemas != '{}')).limit(LIMIT).offset(i).all():
        txt = response.cleaned_content
        stderr = validate_in_memory(txt)

        data = {
            "response_id": response.id,
            "valid": 'Error at' not in stderr,
            "validated_on": datetime.now().isoformat()
        }
        if stderr:
            data.update({
                "errors": [s.strip() for s in stderr.split('\n\n') if s]
            })

        try:
            v = Validation()
            v.create(data)
            loader.load(v)
        except Exception as ex:
            with open('validation_logs.log', 'a') as a:
                a.write('\n{0}: {1}\n\n'.format(response.id, ex))

read_session.close()
