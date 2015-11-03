#!/anaconda/bin/python

from optparse import OptionParser
import json as js
# from mpp.utils import validate_in_memory
from mpp.models import Validation, Response
from datetime import datetime
import traceback
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
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
    op.add_option('--files', '-f')  # comma-delim list, one response id/line
    options, arguments = op.parse_args()

    if not options.connection:
        op.error('No RDS Connection provided')
    if not options.files:
        op.error('No file list')

    with open('big_rds.conf', 'r') as f:
        conf = js.loads(f.read())

    # our connection
    engine = sqla.create_engine(conf.get('connection'))
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    cmd = "StdInParse -v=always -n -s -f < %s"

    for f in options.files.split(','):
        with open(f, 'r') as g:
            data = [int(a.strip()) for a in g.readlines() if a]

        for d in data:
            response = session.query(Response).filter(Response.id == d).first()

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
                status, output, error = tc.run(60)
            except:
                print 'failed validation: ', response_id
                error = 'Error at validation CLI: timeout error'
                # continue
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

            try:
                session.add(v)
                session.commit()
            except Exception as ex:
                print ex
                print d
                print
                session.rollback()
                continue

    session.close()


if __name__ == '__main__':
    main()
