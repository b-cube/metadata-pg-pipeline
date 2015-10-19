import json
import glob
import os
from mpp.loaders import Loader
from mpp.models import Response, Identity
from sqlalchemy.exc import IntegrityError


# subdirs_for_rm = ['identified', 'cleaned']
files = glob.glob(
    '/home/ubuntu/semantics_pipeline/pipeline_tests/identified/*.json')

to_remove = []

with open('local_rds.conf', 'r') as f:
    conf = json.loads(f.read())
loader = Loader(conf)

for i, f in enumerate(files[0:10]):
    with open(f, 'r') as g:
        data = json.loads(g.read())

    fname = f.split('/')[-1].split('_')[0]
    fmt = data.get('response_format', 'unknown')

    try:
        r = Response()
        r.create(data)
        r_id = loader.load(r)
    except IntegrityError:
        # one of the original set of fgdc recs?
        pass
    except:
        continue

    try:
        d = Identity()
        data.update({"response_id": r_id})
        d.create(data)
        loader.load(d)
    except:
        continue

    if fmt != 'xml':
        to_remove.append(fname)
        # for s in subdirs_for_rm:
        #     os.remove('../pipeline_tests/{0}/{1}_s.json'.format(s, fname))
