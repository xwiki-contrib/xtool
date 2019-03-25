# Define a set of utility functions to initialize the environment
import argparse
import logging
import sys

def init_logger(logLevel):
    root = logging.getLogger()

    if (logLevel >= 1):
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[ %(levelname)s ] %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

def parse_args():
    rootParser = argparse.ArgumentParser(prog='x', description='Provide a set of tools to manage local XWiki installations')
    rootParser.add_argument('-v', '--verbose', action='count', default=0, help='enable verbose logs')

    subParsers = rootParser.add_subparsers(dest='action', required=True, help='the action to perform')

    listParser = subParsers.add_parser('list', help='list the managed entities')
    listParser.add_argument('entity', help='the type of entity to list')

    downloadParser = subParsers.add_parser('download', help='download a new version')
    downloadParser.add_argument('version', help='the XWiki version to download')

    createParser = subParsers.add_parser('create', help='create a new instance')
    createParser.add_argument('instance_name', help='the name of the instance to create')
    createParser.add_argument('version', help='the XWiki version to use in the instance')

    startParser = subParsers.add_parser('start', help='start an instance')
    startParser.add_argument('instance_name',
                             nargs='?',
                             default=None,
                             help='the name of the instance to start')
    startParser.add_argument('-d', '--debug', action='store_true', help='toggle debug mode')

    removeParser = subParsers.add_parser('remove', help='remove an entity')
    removeParser.add_argument('instance_name', help='the name of the instnace to remove')

    return rootParser.parse_args()
