#!/anaconda/bin/python

from optparse import OptionParser
import json as js
from mpp.utils import validate_in_memory
from mpp.models import Validation, Response
from datetime import datetime
import traceback
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_


def main():
    op = OptionParser()
    op.add_option('--connection', '-c')
    op.add_option('--start', '-s')
    op.add_option('--end', '-e')
    op.add_option('--interval', '-i')
    options, arguments = op.parse_args()

    if not options.connection:
        op.error('No RDS Connection provided')

    try:
        LIMIT = int(options.interval)
        s = int(options.start)
        e = int(options.end)
    except Exception as ex:
        op.error('Invalid pagination integer: {0}'.format(ex))

    with open('big_rds.conf', 'r') as f:
        conf = js.loads(f.read())

    # our connection
    engine = sqla.create_engine(conf.get('connection'))
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    for OFFSET in xrange(s, e, LIMIT):
        appends = []
        for response_id, cleaned_content in session.query(Response.id, Response.cleaned_content).filter(
                and_(Response.schemas is not None, Response.schemas != '{}')).limit(LIMIT).offset(OFFSET).all():

            stderr = validate_in_memory(cleaned_content)

            validated_data = {
                "response_id": response_id,
                "valid": 'Error at' not in stderr,
                "validated_on": datetime.now().isoformat()
            }
            if stderr:
                validated_data.update({
                    "errors": [v.strip() for v in stderr.split('\n\n') if v]
                })

            v = Validation()
            v.create(validated_data)
            appends.append(v)

        try:
            session.add_all(appends)
            session.commit()
        except Exception as ex:
            print ex
            print [a['response_id'] for a in appends]
            print
            session.rollback()
            continue

        with open('validated/{0}.json'.format('_'.join([str(a['response_id'] )for a in appends])), 'w') as g:
            g.write(js.dumps([a.to_json() for a in appends], indent=4))

    session.close()

if __name__ == '__main__':
    main()
