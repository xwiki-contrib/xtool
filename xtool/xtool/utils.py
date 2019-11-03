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


def valid_config(configArg):
    upperArg = str(configArg).lower()
    if upperArg in ['true']:
        return True
    elif upperArg in ['false']:
        return False
    else:
        return configArg


def parse_args():
    rootParser = argparse.ArgumentParser(prog='x',
                                         description='Provide a set of tools to manage local XWiki installations')
    rootParser.add_argument('-v', '--verbose', action='count', default=0, help='enable verbose logs')

    subParsers = rootParser.add_subparsers(dest='action', required=True, help='the action to perform')

    listParser = subParsers.add_parser('list', help='list the managed entities')
    listParser.add_argument('entity', help='the type of entity to list')

    downloadParser = subParsers.add_parser('download', help='download a new version')
    downloadParser.add_argument('version', help='the XWiki version to download')

    configParser = subParsers.add_parser('config', help='view or edit the tool configuration')
    configParser.add_argument('property_name', help='the name of the property')
    configParser.add_argument('-s', '--set', metavar='VALUE', type=valid_config, help='set the value of the property')

    createParser = subParsers.add_parser('create', help='create a new instance')
    createParser.add_argument('instance_name', help='the name of the instance to create')
    createParser.add_argument('version', help='the XWiki version to use in the instance')

    editParser = subParsers.add_parser('edit', help='edit a file in the given instance')
    editParser.add_argument('instance_name', help='the name of the instance to use')
    editParser.add_argument('file', help='the name of the file to edit')

    copyParser = subParsers.add_parser('copy', help='copy an instance')
    copyParser.add_argument('instance_name', help='the name of the instance to copy')
    copyParser.add_argument('new_instance_name', help='the new name of the instance')

    snapshotParser = subParsers.add_parser('snapshot', help='manage instance snapshots')
    snapshotParser.add_argument('snapshot_action', choices=['create', 'restore'], help='the action to perform')
    snapshotParser.add_argument('entity_name',
                                help='the name of the instance to snapshot or the name of the snapshot to restore')
    snapshotParser.add_argument('-o', '--overwrite', action='store_true',
                                help='overwrite an existing instance if needed')

    startParser = subParsers.add_parser('start', help='start an instance')
    startParser.add_argument('entity_name',
                             nargs='?',
                             default=None,
                             help='the name of the instance or version (if --temp) to start')
    startParser.add_argument('-d', '--debug', action='store_true', help='toggle debug mode')
    startParser.add_argument('-t', '--temp', action='store_true', help='start a temporary instance')

    removeParser = subParsers.add_parser('remove', help='remove an entity')
    removeParser.add_argument('instance_name', help='the name of the instnace to remove')

    return rootParser.parse_args()
