#!/anaconda/bin/python

import json
from mpp.loaders import Loader
from mpp.readers import ResponseReader
from mpp.utils import validate_in_memory
from mpp.models import Validation
from datetime import datetime
import traceback

'''
geared to validate just the federal responses
from the wee little metadata ec2, reading
and writing to rds
'''
# set up the connection
with open('local_rds.conf', 'r') as f:
    conf = json.loads(f.read())
reader = ResponseReader(conf)

loader = Loader(conf)

# get the set, validate, store outputs
for response in reader.read(''):
    print response.source_url

    xml = response.cleaned_content
    stderr = validate_in_memory(xml)

    data = {
        "response_id": response.id,
        "valid": 'Fatal Error' not in stderr,
        "validated_on": datetime.now()
    }
    if stderr:
        data.update({
            "errors": [s.strip() for s in stderr.split('\n\n')]
        })
        print '\t', stderr[:100]

    try:
        v = Validation()
        v.create(data)
        loader.load(v)
    except Exception as ex:
        print ex
