# load the solr docs into the remote rds
from optparse import OptionParser
import glob
import json
import os
from lib.loaders import Loader
import logging


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def main():
    op = OptionParser()
    # a postgres config
    op.add_option('--config', '-c')
    # path to the docs to load
    op.add_option('--documents', '-d')

    options, arguments = op.parse_args()

    docs = glob.glob(os.path.join(options.documents, '*.json'))
    if not docs:
        op.error('Empty documents directory')

    config = options.config
    connection_string = config.get('connection_string')
    loader = Loader(connection_string)
    for doc in docs:
        with open(doc, 'rb') as f:
            data = json.loads(f.read())

        loader.load(data)

if __name__ == '__main__':
    main()
