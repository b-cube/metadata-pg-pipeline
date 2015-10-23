
# coding: utf-8

import glob
import re
from datetime import datetime
import dateutil.parser as dateparser
from itertools import chain

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import WordListCorpusReader

from semproc.rawresponse import RawResponse
from semproc.bag_parser import BagParser

import json as js  # name conflict with sqla
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import *
from sqlalchemy import and_
from mpp.models import Response
from mpp.models import BagOfWords

import warnings
warnings.filterwarnings('ignore')


# In[25]:

def convert_header_list(headers):
    '''
    convert from the list of strings, one string
    per kvp, to a dict with keys normalized
    '''
    return dict(
        (k.strip().lower(), v.strip()) for k, v in (
            h.split(':', 1) for h in headers)
    )


def remove_stopwords(text):
    '''
    remove any known english stopwords from a
    piece of text (bag of words or otherwise)
    '''
    _stopwords = set(stopwords.words('english'))
    words = word_tokenize(text)
    words = words if isinstance(words, list) else words.split()
    return ' '.join([w for w in words if w not in _stopwords and w])


def load_token_list(term_file):
    '''
    load some stopword list from the corpus
    '''
    __location__ = '../corpora/'
    tokens = WordListCorpusReader(__location__, term_file)
    return [w.replace('+', '\+') for w in tokens.words()]


def remove_tokens(term_file, text):
    '''
    do this before something like tokenize or the
    resplit option will split the mimetypes to not
    be recognizable as such anymore
    '''
    words = load_token_list(term_file)

    pttn = re.compile('|'.join(words))
    return pttn.sub('', text)

def remove_numeric(text):
    match_pttn = ur'\w*\b-?\d\s*\w*'
    captures = re.findall(match_pttn, u' {0} '.format(text))

    # strip them out
    if captures:
        text = re.sub('|'.join(captures), ' ', text)
        return '' if text == '0' else text

    return text

def strip_dates(text):
        # this should still make it an invalid date
        # text = text[3:] if text.startswith('NaN') else text
        try:
            d = dateparser.parse(text)
            return ''
        except ValueError:
            return text
        except OverflowError:
            return text
        
def strip_filenames(text):
    # we'll see
    exts = ('png', 'jpg', 'hdf', 'xml', 'doc', 'pdf', 'txt', 'jar', 'nc', 'XSL', 'kml', 'xsd')
    return '' if text.endswith(exts) else text
    
def strip_identifiers(texts):
    # chuck any urns, urls, uuids
    _pattern_set = [
        ('url', ur"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""),
        # a urn that isn't a url
        ('urn', ur"(?![http://])(?![https://])(?![ftp://])(([a-z0-9.\S][a-z0-9-.\S]{0,}\S:{1,2}\S)+[a-z0-9()+,\-.=@;$_!*'%/?#]+)"),
        ('uuid', ur'([a-f\d]{8}(-[a-f\d]{4}){3}-[a-f\d]{12}?)'),
        ('doi', ur"(10[.][0-9]{4,}(?:[/][0-9]+)*/(?:(?![\"&\\'])\S)+)"),
        ('md5', ur"([a-f0-9]{32})")
    ]
    for pattern_type, pattern in _pattern_set:
        for m in re.findall(re.compile(pattern), texts):
            m = max(m) if isinstance(m, tuple) else m
            try:
                texts = texts.replace(m, '')
            except Exception as ex:
                print ex
                print m
                
    files = ['cat_interop_urns.txt', 'mimetypes.txt', 'namespaces.txt']
    for f in files:
        texts = remove_tokens(f, texts)
    return texts.split()

def remove_punctuation(text):
    simple_pattern = r'[;|>+:=.,()/?!\[\]{}]'
    text = re.sub(simple_pattern, ' ', text)
    text = text.replace(' - ', ' ').strip()
    return text if text != '-' else ''

def strip_punctuation(text):
    terminal_punctuation = '(){}[].,~|":'
    return text.strip(terminal_punctuation).strip()
    
def clean(text):
    text = strip_dates(text)
    text = remove_numeric(text)
    
    text = remove_punctuation(text.strip()).strip()
    text = strip_punctuation(text)
    
    text = strip_filenames(text)
    
    return text
        
exclude_tags = ['schemaLocation', 'noNamespaceSchemaLocation']


# In[26]:

# grab the clean text from the rds
with open('../local/big_rds.conf', 'r') as f:
    conf = js.loads(f.read())

# our connection
engine = sqla.create_engine(conf.get('connection'))
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


# In[27]:

# get a count of the xml responses
total = session.query(Response).filter(Response.format=='xml').count()


# In[ ]:

LIMIT = 100

# total = 5
# LIMIT= total

for i in xrange(0, total, LIMIT):
    # get some responses
    responses = session.query(Response).filter(Response.format=='xml').limit(LIMIT).offset(i).all()
    
    appends = []
    
    for response in responses:
        cleaned_content = response.cleaned_content
        
        # strip the html cruft but ignore the a tags
        bp = BagParser(cleaned_content.encode('utf-8'), True, False)
        if bp.parser.xml is None:
            print 'NOT XML: ', cleaned_content[:100]
            continue
        # we don't care about the fully qualified namespace here
        stripped_text = [b[1].split() for b in bp.strip_text(exclude_tags) if b[1]]
        stripped_text = list(chain.from_iterable(stripped_text))
        cleaned_text = [s for s in stripped_text if clean(s)]

        bow = strip_identifiers(' '.join(cleaned_text))
        
        bag = BagOfWords(
            generated_on=datetime.now().isoformat(),
            bag_of_words=bow,
            method="basic",
            response_id=response.id
        )
        appends.append(bag)
    
    try:
        session.add_all(appends)
        session.commit()
    except Exception as ex:
        print 'failed ', i, ex
        session.rollback()
    
session.close()
