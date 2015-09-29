#!/anaconda/bin/python

import json
from mpp.loaders import Loader
import traceback

'''

'''
# set up the connection
with open('local_rds.conf', 'r') as f:
    conf = json.loads(f.read())
loader = Loader(conf)

with open('responses_with_federal_schemas.txt', 'r') as f:
    responses = [g.strip() for g in f.readlines() if g]

for response in responses[:10]:
    with open(response, 'r') as f:
        data = json.loads(f.read())

    try:
        loader.load(data)
    except Exception as ex:
        print response
        print '\t', ex
        traceback.print_exc()
