# Define a set of utility functions to initialize the environment
import argparse
import binascii
import logging
import os
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


def random_chars(numberOfChars):
    return binascii.b2a_hex(os.urandom(numberOfChars)).decode('UTF-8')


def tqdm_download_hook(t):
    # Code snippet taken from
    # https://github.com/tqdm/tqdm/blob/cd7f61b4562fb2f4aad560edf094a2ddad1ae3b7/examples/tqdm_wget.py#L28
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        if tsize not in (None, -1):
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return update_to


def parse_args():
    rootParser = argparse.ArgumentParser(
        prog='x',
        description=('Provide a set of tools to manage local XWiki installations. '
                     'To get more information about a specific command, use `x <command> -h`')
    )
    rootParser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='enable verbose logs on the tool itself, mostly used for debugging purposes'
    )

    subParsers = rootParser.add_subparsers(dest='action', required=True, help='the action to perform')

    # List action
    listParser = subParsers.add_parser(
        'list',
        help=('list the managed entities, an entity can be an instance, '
              'a version of XWiki or even a snapshot of an instance')
    )
    listParser.add_argument('entity', choices=['instances', 'versions', 'snapshots'],
                            help='the type of entity to list')

    # Download action
    downloadParser = subParsers.add_parser('download', help='download a new version')
    downloadParser.add_argument('version', help='the XWiki version to download')

    # Config action
    configParser = subParsers.add_parser('config', help='view or edit the tool configuration')
    configParser.add_argument('property_name', help='the name of the property')
    configParser.add_argument('-s', '--set', metavar='VALUE', type=valid_config, help='set the value of the property')

    # Create action
    createParser = subParsers.add_parser('create', help='create a new instance')
    createParser.add_argument('instance_name', help='the name of the instance to create')
    createParser.add_argument('version', help='the XWiki version to use in the instance')

    # Edit action
    editParser = subParsers.add_parser(
        'edit',
        help=('edit a file in the given instance, by default, xtool will search or the file in the WEB-INF '
              'folder of the instance')
    )
    editParser.add_argument('instance_name', help='the name of the instance to use')
    editParser.add_argument('file', help='the name of the file to edit, for example : `xwiki.cfg` or `hibernate.xml`')

    # Copy action
    copyParser = subParsers.add_parser('copy', help='copy an instance')
    copyParser.add_argument('instance_name', help='the name of the instance to copy')
    copyParser.add_argument('new_instance_name', help='the new name of the instance')

    # Snapshot action
    snapshotParser = subParsers.add_parser('snapshot', help='manage instance snapshots')
    snapshotParser.add_argument('snapshot_action', choices=['create', 'restore'], help='the action to perform')
    snapshotParser.add_argument(
        'entity_name',
        help='the name of the instance to snapshot or the name of the snapshot to restore'
    )
    snapshotParser.add_argument('-o', '--overwrite', action='store_true',
                                help='overwrite an existing instance if needed')

    # Upgrade action
    upgradeParser = subParsers.add_parser('upgrade', help='upgrade an existing instance to a newer version')
    upgradeParser.add_argument('instance_name', help='the name of the instance to upgrade')
    upgradeParser.add_argument('version', help='the version to which the instance should be upgraded')

    # Start action
    startParser = subParsers.add_parser(
        'start',
        help='start an instance'
    )
    startParser.add_argument(
        'entity_name',
        nargs='?',
        default=None,
        help='the name of the instance or version (if --temp) to start'
    )
    startParser.add_argument('-d', '--debug', action='store_true', help='toggle debug mode')
    startParser.add_argument(
        '-p', '--port',
        help='specify a port on which the instance should be started'
    )
    startParser.add_argument(
        '-t', '--temp',
        action='store_true',
        help=('start a temporary instance: xtool will create a random instance name with the given version and start '
              'it. The instance will be removed automatically after being killed.')
    )

    # Remove action
    removeParser = subParsers.add_parser('remove', help='remove an entity')
    removeParser.add_argument('-i', '--instance', action='store_true', help='remove an instance')
    removeParser.add_argument('entity_name', help='the name of the entity to remove')

    # Entity-related parsers
    instanceParser = subParsers.add_parser('instance', help='manage instances')

    versionParser = subParsers.add_parser('version', help='manage versions')

    return rootParser.parse_args()
