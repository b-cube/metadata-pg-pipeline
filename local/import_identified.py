import json
import glob
import os
from mpp.loaders import Loader
from mpp.models import Response, Identity
from sqlalchemy.exc import IntegrityError


files = glob.glob(
    '/home/ubuntu/semantics_pipeline/pipeline_tests/identified/*.json')

with open('local_rds.conf', 'r') as f:
    conf = json.loads(f.read())
loader = Loader(conf)

for i, f in enumerate(files[100:]):
    with open(f, 'r') as g:
        data = json.loads(g.read())

    fname = f.split('/')[-1].split('_')[0]
    fmt = data.get('response_datatype', 'unknown')
    identity = data.get('identity', [])

    try:
        r = Response()
        r.create(data)
        r_id = loader.load(r)
    except Exception as ex:
        print fname, ex
        continue

    if identity and r_id:
        try:
            d = Identity()
            data.update({"response_id": r_id})
            d.create(data)
            loader.load(d)
        except:
            continue
