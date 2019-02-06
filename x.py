#!/usr/bin/env python3
import argparse
import logging

from configuration import ConfigManager
from instances import InstanceManager
from versions import VersionManager
from utils import initRootLogger

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
startParser.add_argument('instance_name', help='the name of the instance to start')
startParser.add_argument('-d', '--debug', action='store_true', help='toggle debug mode')

removeParser = subParsers.add_parser('remove', help='remove an entity')
removeParser.add_argument('instance_name', help='the name of the instnace to remove')

args = rootParser.parse_args()

initRootLogger(args.verbose)
logger = logging.getLogger('Main')

cm = ConfigManager()
vm = VersionManager(cm)
im = InstanceManager(cm, vm)

logger.debug('Arguments : {}'.format(args))
if ('list'.startswith(args.action)):
    if ('versions'.startswith(args.entity)):
      print(cm.versions())
    elif ('instances'.startswith(args.entity)):
      print(cm.instances())
elif ('download'.startswith(args.action)):
    vm.download(args.version)
elif ('create'.startswith(args.action)):
    im.create(args.instance_name, args.version)
elif ('start'.startswith(args.action)):
    im.start(args.instnace_name, args.debug)
elif ('remove'.startswith(args.action)):
    im.remove(args.instance_name)
