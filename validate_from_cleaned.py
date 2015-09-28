import json
from optparse import OptionParser


'''
query the aws rds
for each object, get the cleaned xml
validate
capture the errors - post to rds
'''


def main():
    # query postgres for x(response.id, sha, xml_as_string)
    # validate the in-memory xml from the query
    # deal with the outputs
    # post to postgres
    op = OptionParser()
    op.add_option('--connection', '-c')
    # this is going to have to be structured & limited
    op.add_option('--query', '-q')
    op.add_option('--directory', '-d')

    options, arguments = op.parse_args()

    # so hit our metadata-pg cli to make the query

    # TODO: convert to a multiprocessing widget

if __name__ == '__main__':
    main()
