#!/anaconda/bin/python

from optparse import OptionParser
import json as js
# from mpp.utils import validate_in_memory
from mpp.models import Validation, Response
from datetime import datetime
import traceback
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import subprocess
import threading
import tempfile
from os import write, close, unlink


class TimedCmd(object):
    out, err = '', ''
    status = None
    process = None
    command = None

    def __init__(self, cmd):
        self.command = cmd

    def run(self, timeout=None):
        def target():
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.out, self.err = self.process.communicate()
            self.status = self.process.returncode

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            try:
                self.process.terminate()
                thread.join()
            except OSError, e:
                return -1, '', e
            raise RuntimeError('Subprocess timed out')
        return self.status, self.out, self.err


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

    cmd = "StdInParse -v=always -n -s -f < %s"

    for OFFSET in xrange(s, e, LIMIT):
        appends = []
        for response in session.query(Response).filter(
                and_(Response.schemas is not None, Response.schemas != '{}')
            ).limit(LIMIT).offset(OFFSET).all():

            if response.validations:
                continue

            response_id = response.id
            cleaned_content = response.cleaned_content

            handle, name = tempfile.mkstemp(suffix='.xml')
            write(handle, cleaned_content)
            close(handle)

            # stderr = validate_in_memory(cleaned_content)
            tc = TimedCmd(cmd % name)
            try:
                status, output, error = tc.run(120)
            except:
                print 'failed validation: ', response_id
                continue
            finally:
                unlink(name)

            validated_data = {
                "response_id": response_id,
                "valid": 'Error at' not in error,
                "validated_on": datetime.now().isoformat()
            }
            if error:
                validated_data.update({
                    "errors": [v.strip() for v in error.split('\n\n') if v]
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

        with open('validated/{0}.json'.format('_'.join([str(a.response_id) for a in appends])), 'w') as g:
            g.write(js.dumps([a.to_json() for a in appends], indent=4))

    session.close()

if __name__ == '__main__':
    main()
