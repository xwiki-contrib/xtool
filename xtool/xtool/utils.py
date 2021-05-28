# Define a set of utility functions to initialize the environment
import argparse
import binascii
import hashlib
import logging
import os
import sys

from version.parser import VersionParser
from instance.parser import InstanceParser
from snapshot.parser import SnapshotParser


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


# Return the MD5 sum of a file
def compute_checksum(path):
    with open(path, 'rb') as f:
        digest = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:  # In case we're at the end of the file
                break
            digest.update(data)
        return digest.hexdigest()


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
        aliases=['l'],
        help=('list the managed entities, an entity can be an instance, '
              'a version of XWiki or even a snapshot of an instance')
    )
    listParser.add_argument('entity', choices=['instances', 'versions', 'snapshots'],
                            help='the type of entity to list')

    # Top-level actions proposed by entities
    VersionParser.addActions(subParsers, topLevel=True)
    InstanceParser.addActions(subParsers, topLevel=True)
    SnapshotParser.addActions(subParsers, topLevel=True)

    # Config action
    configParser = subParsers.add_parser('config', help='view or edit the tool configuration')
    configParser.add_argument('property_name', help='the name of the property')
    configParser.add_argument('-s', '--set', metavar='VALUE', type=valid_config, help='set the value of the property')

    # Entity-related parsers
    versionParser = subParsers.add_parser('version', aliases=['v'], help='manage versions')
    versionSubParsers = versionParser.add_subparsers(dest='subAction', required=True, help='the action to perform')
    VersionParser.addActions(versionSubParsers)

    instanceParser = subParsers.add_parser('instance', aliases=['i'], help='manage instances')
    instanceSubParsers = instanceParser.add_subparsers(dest='subAction', required=True, help='the action to perform')
    InstanceParser.addActions(instanceSubParsers)

    snapshotParser = subParsers.add_parser('snapshot', aliases=['sp'], help='manage instance snapshots')
    snapshotSubParsers = snapshotParser.add_subparsers(dest='subAction', required=True, help='the action to perform')
    SnapshotParser.addActions(snapshotSubParsers)

    return rootParser.parse_args()
