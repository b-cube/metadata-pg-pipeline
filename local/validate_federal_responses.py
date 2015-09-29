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
    xml = response.cleaned_content
    stderr = validate_in_memory(xml)

    data = {
        "response_id": response.id,
        "valid": stderr != '',
        "validated_on": datetime.now()
    }
    if stderr:
        data.update({
            "errors": stderr.split('\n\n')
        })

    v = Validation()
    v.create(data)
    loader.load(v)
