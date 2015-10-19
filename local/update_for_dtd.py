from lxml import etree
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
import json
from mpp.models import Response

'''
update the response objs if xml so
that the schemas list includes the dtd
if one exists
'''

with open('big_rds.conf', 'r') as f:
    conf = json.loads(f.read())

# our connection
engine = sqla.create_engine(conf.get('connection'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

with open('potential_dtd_responses.txt', 'r') as f:
    response_ids = [l.strip() for l in f.readlines() if l]


def get_dtd(txt):
    try:
        xml = etree.fromstring(txt.encode('utf-8'))
    except:
        return ''

    docinfo = xml.getroottree().docinfo
    return docinfo.system_url

for i, response_id in enumerate(response_ids):
    if i % 10000 == 0:
        print 'finished', i

    response = session.query(Response).filter(
        Response.id == response_id).first()
    cleaned_content = response.cleaned_content

    dtd = get_dtd(cleaned_content)

    if dtd:
        try:
            s = response.schemas
            s = s if s else []
            response.schemas = s + [dtd] if dtd not in s else []
            session.commit()
        except:
            session.rollback()

session.close()
